import logging
import time

from django.conf import settings

logger = logging.getLogger(__name__)


class SpotifyClient:
    """Spotify Web API client using Client Credentials flow."""

    _token = None
    _token_expires = 0

    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    API_BASE = 'https://api.spotify.com/v1'

    def is_available(self):
        return bool(
            getattr(settings, 'SPOTIFY_CLIENT_ID', '')
            and getattr(settings, 'SPOTIFY_CLIENT_SECRET', '')
        )

    def _get_token(self):
        if SpotifyClient._token and time.time() < SpotifyClient._token_expires:
            return SpotifyClient._token

        import requests

        try:
            resp = requests.post(
                self.TOKEN_URL,
                data={'grant_type': 'client_credentials'},
                auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            SpotifyClient._token = data['access_token']
            SpotifyClient._token_expires = time.time() + data.get('expires_in', 3600) - 60
            return SpotifyClient._token
        except Exception as e:
            logger.error(f'Spotify token error: {e}')
            return None

    def search_tracks(self, query, limit=5):
        token = self._get_token()
        if not token:
            return []

        import requests

        try:
            resp = requests.get(
                f'{self.API_BASE}/search',
                params={'q': query, 'type': 'track', 'limit': limit, 'market': 'JP'},
                headers={'Authorization': f'Bearer {token}'},
                timeout=5,
            )
            resp.raise_for_status()
            tracks = resp.json().get('tracks', {}).get('items', [])
            return [
                {
                    'spotify_id': t['id'],
                    'title': t['name'],
                    'artist': ', '.join(a['name'] for a in t['artists']),
                    'album_art_url': t['album']['images'][0]['url'] if t['album']['images'] else '',
                }
                for t in tracks
            ]
        except Exception as e:
            logger.error(f'Spotify track search error: {e}')
            return []

    def search_artists(self, query, limit=5):
        token = self._get_token()
        if not token:
            return []

        import requests

        try:
            resp = requests.get(
                f'{self.API_BASE}/search',
                params={'q': query, 'type': 'artist', 'limit': limit, 'market': 'JP'},
                headers={'Authorization': f'Bearer {token}'},
                timeout=5,
            )
            resp.raise_for_status()
            artists = resp.json().get('artists', {}).get('items', [])
            return [
                {
                    'spotify_artist_id': a['id'],
                    'name': a['name'],
                    'image_url': a['images'][0]['url'] if a['images'] else '',
                    'genres': a.get('genres', [])[:3],
                }
                for a in artists
            ]
        except Exception as e:
            logger.error(f'Spotify artist search error: {e}')
            return []
