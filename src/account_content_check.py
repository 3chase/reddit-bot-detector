from src.i_detection_rule import IDecetionRule
#from detection_result import DetectionResults archived
import praw
from thefuzz import fuzz
from googleapiclient.discovery import build
import os
from time import sleep
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

"""Add total amount of activity, and posts comments containing links"""


"""To be refactored using ArcticShift Api"""
class SearchReddit:
    def __init__(self, reddit_name: str, comments: list[str], praw_instance: praw.Reddit):
        self.reddit_name = reddit_name
        self.comments = comments
        self.praw_instance = praw_instance
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cx = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        if self.api_key:
            self.service = build("customsearch", "v1", developerKey=self.api_key)
        else:
            self.service = None
    def __match_copy__(self):
        if not self.service:
            print("Error: Google API key or Search Engine ID not found in .env file.")
            return {}
        copied_results = {}
        for comment in self.comments:
            if len(comment) < 20:
                continue
            copied_results[comment] = [] 
            try:
                sleep(1)
                query = f'site:reddit.com "{comment}"'
                res = self.service.cse().list(q=query, cx=self.cx, num=2).execute()
                urls_from_google = []
                if 'items' in res:
                    for item in res['items']:
                        urls_from_google.append(item['link'])
                for url in urls_from_google:
                    try:
                        submission = self.praw_instance.submission(url=url)
                        submission.comment_sort = "top"
                        submission.comments.replace_more(limit=0)
                        for top_level_comment in submission.comments.list()[:20]:
                            if not hasattr(top_level_comment, 'author') or top_level_comment.author is None:
                                continue
                            score = fuzz.ratio(comment, top_level_comment.body)
                            if score >= 85 and top_level_comment.author.name != self.reddit_name:
                                copy_details = {
                                    "copy_author": top_level_comment.author.name,
                                    "subreddit": top_level_comment.subreddit.display_name,
                                    "link": f"https://www.reddit.com{top_level_comment.permalink}",
                                    "created_utc": top_level_comment.created_utc
                                }
                                copied_results[comment].append(copy_details)
                                # Break once we find a match in this submission
                                break
                    except Exception as e:
                        print(f"Could not process URL {url}. Error: {e}")
            except Exception as e:
                print(f"An API search error occurred for comment: '{comment[:50]}...'")
                print(f"Error: {e}")     
        return copied_results
    def execute_matches(self):
        return self.__match_copy__()
    

class AccountContentCheck(IDecetionRule):
    """
    This class gets related information of a user relating with the content of a users comments

    Attributes:
        reddit_name (str): Returns the name of the user's account
        comments (list[str]): Returns the list of the accounts 50 most recent comments
        praw_instance (praw.Reddit): An authenticated PRAW Reddit instance

    Values the class finds:
        1. The ratio of comments under 20 characters to the total amount of comments
        2. The pairwise similarity score of the 10 most recent comments on a user's account
        3. Checks the 3 most recent comments to see if they had been plagiarized from another user
    """
    def __init__(self, reddit_name: str, comments: list[str], post_titles: list[str], praw_instance: praw.Reddit):
        self.reddit_name = reddit_name
        self.comments = comments
        self.post_titles = post_titles
        self.praw_instance = praw_instance

        #cut offs for hueristics  
        self.SHORT_COMMENT_RATIO = 0.2

    def __check_length_comments__(self):
        SHORT_CUTOFF = 20
        if not self.comments:
            return 0
        short = 0
        for comment in self.comments:
            if len(comment) < SHORT_CUTOFF:
                short += 1
        return short / len(self.comments)
    
    def __get_average_comment_similarity__(self):
        """Finds the linguistic similarity of a users most recent COMMENT_LIMIT comments
        """
        COMMENT_LIMIT = 15
        if len(self.comments) < 2:
            return 0.0
        if(len(self.comments) >= COMMENT_LIMIT):
            first_x_comments = self.comments[:COMMENT_LIMIT]
        else:
            first_x_comments = self.comments
        vectorizer = TfidfVectorizer(stop_words='english') #Uses Term Frequency and Inverse Document Frequency
        tfidf_matrix = vectorizer.fit_transform(first_x_comments)
        cosine_sim_matrix = cosine_similarity(tfidf_matrix) #Finds similarity between each comment
        upper_triangle_indices = np.triu_indices(len(first_x_comments), k=1) #Uses upper triangle to avoid reduntant comparisons
        pairwise_similarity_scores = cosine_sim_matrix[upper_triangle_indices]
        if pairwise_similarity_scores.size == 0:
            return 0.0
        return pairwise_similarity_scores.mean() #returns average of the scores
    
    #returns the duplicated top comments based on the users recent X comments    
    def __check_repeated_comments__(self):
        """Finds COMMENT_LIMIT comments that are plagiarized using the SearchReddit class
        """
        COMMENT_LIMIT = 3
        if(len(self.comments) >= COMMENT_LIMIT):
            first_x_comments = self.comments[:COMMENT_LIMIT]
        else:
            first_x_comments = self.comments
        searcher = SearchReddit(self.reddit_name, first_x_comments, self.praw_instance)
        matches = searcher.execute_matches()
        return {k: v for k, v in matches.items() if v}
    
    def get_features(self) -> dict:
        features = {
            "short_comment_ratio": self.__check_length_comments__(),
            "avg_comment_similarity": self.__get_average_comment_similarity__()
        }
        return features
    


    """
    def execute_check(self) -> DetectionResults:
        rule_name = "Account of short or similair comments check"
        short_comment_ratio = self.__check_length_comments__() 
        matches = self.__check_repeated_comments__()
        num_matches = len(matches)
        details = []
        score_from_short_comments = short_comment_ratio * 0.8
        if score_from_short_comments > self.SHORT_COMMENT_RATIO:
            details.append(f"About {short_comment_ratio:.0%} of comments are short.")
        score_from_copies = 0
        if num_matches == 1:
            score_from_copies = 0.3
        elif num_matches == 2:
            score_from_copies = 0.7
        elif num_matches > 2:
            score_from_copies = 1.0
        if num_matches > 0:
            details.append(f"Found {num_matches} comment(s) that appear to be copied from other users.")
        confidence_score = score_from_short_comments + score_from_copies
        confidence_score = min(confidence_score, 1.0)
        is_suspicious = confidence_score > 0.5
        results = DetectionResults(
            rule_name = rule_name,
            is_suspicious = is_suspicious,
            confidence_score = confidence_score,
            details = " ".join(details)
        )
        return(results)
        
"""
        
    