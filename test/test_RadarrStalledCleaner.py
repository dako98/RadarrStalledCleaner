import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import timedelta as tdelta
from datetime import datetime as dt

import RadarrStalledCleaner as RadarrStalledCleaner


class TestMain(unittest.TestCase):

    @patch("src.RadarrStalledCleaner.RadarrAPI")
    def test_remaining_time_exceeded(self, mock_radarr_api):
        """Tests the main function when the remaining time is exceeded.

        Args:
            mock_radarr_api (MagicMock): A mock of the RadarrAPI class.
        """

        # Mock data
        late_completion_time = (dt.now() + tdelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
        grab_time = (dt.now() - tdelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
        queued_movies = [
            {
                "movieId": 1,
                "id": 1,
                "title": "Movie Title",
                "status": "downloading",
                "estimatedCompletionTime": late_completion_time,
            }
        ]
        grab_events = [{"date": grab_time, "id": 1}]

        # Create a mock instance of RadarrAPI
        mock_radarr_api_instance = MagicMock()

        # Configure the mock instance to return specific data when its methods are called
        mock_radarr_api_instance.get_queue_details.return_value = queued_movies
        mock_radarr_api_instance.get_movie_history.return_value = grab_events
    
        # Set the RadarrAPI constructor to return the mock instance
        mock_radarr_api.return_value = mock_radarr_api_instance

        # Run the script
        RadarrStalledCleaner.main(sys.argv)

        self.assertEqual(mock_radarr_api.return_value.del_queue.call_count, 1)
    
    @patch("src.RadarrStalledCleaner.RadarrAPI")
    def test_remaining_time_not_exceeded(self, mock_radarr_api):
        """Tests the main function when the remaining time is not exceeded.

        Args:
            mock_radarr_api (MagicMock): A mock of the RadarrAPI class.
        """
        # Mock data
        normal_completion_time = (dt.now() + tdelta(hours=3)).strftime('%Y-%m-%dT%H:%M:%SZ')
        grab_time = (dt.now() - tdelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
        queued_movies = [
            {
                "movieId": 1,
                "id": 1,
                "title": "Movie Title",
                "status": "downloading",
                "estimatedCompletionTime": normal_completion_time,
            }
        ]
        grab_events = [{"date": grab_time, "id": 1}]

        # Create a mock instance of RadarrAPI
        mock_radarr_api_instance = MagicMock()

        # Configure the mock instance to return specific data when its methods are called
        mock_radarr_api_instance.get_queue_details.return_value = queued_movies
        mock_radarr_api_instance.get_movie_history.return_value = grab_events
    
        # Set the RadarrAPI constructor to return the mock instance
        mock_radarr_api.return_value = mock_radarr_api_instance

        # Run the script
        RadarrStalledCleaner.main(sys.argv)

        self.assertEqual(mock_radarr_api.return_value.del_queue.call_count, 0)

    @patch("src.RadarrStalledCleaner.RadarrAPI")
    def test_hard_time_limit_exceeded(self, mock_radarr_api):
        """Tests the main function when the hard time limit is exceeded.

        Args:
            mock_radarr_api (MagicMock): A mock of the RadarrAPI class.
        """
        # Mock data
        normal_completion_time = (dt.now() + tdelta(hours=3)).strftime('%Y-%m-%dT%H:%M:%SZ')
        grab_time = (dt.now() - tdelta(days=2, hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ') # Overdue by more than 2 days
        queued_movies = [
            {
                "movieId": 1,
                "id": 1,
                "title": "Movie Title",
                "status": "downloading",
                "estimatedCompletionTime": normal_completion_time, 
            }
        ]
        grab_events = [{"date": grab_time, "id": 1}]

        # Create a mock instance of RadarrAPI
        mock_radarr_api_instance = MagicMock()

        # Configure the mock instance to return specific data when its methods are called
        mock_radarr_api_instance.get_queue_details.return_value = queued_movies
        mock_radarr_api_instance.get_movie_history.return_value = grab_events
    
        # Set the RadarrAPI constructor to return the mock instance
        mock_radarr_api.return_value = mock_radarr_api_instance

        # Run the script
        RadarrStalledCleaner.main(sys.argv)

        # Check that the del_queue method was called once
        self.assertEqual(mock_radarr_api.return_value.del_queue.call_count, 1)


if __name__ == "main":
    unittest.main()
