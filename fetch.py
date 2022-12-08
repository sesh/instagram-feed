import json
import sys

from requests_html import HTMLSession


class InstagramFeed:

    def __init__(self, username):
        self.username = username
        self.html = self.fetch_html()

    def generate(self):
        return {
            'version': 'https://jsonfeed.org/version/1',
            'title': self.get_title(),
            'url': self.get_homepage_url(),
            'author': self.get_author_block(),
            'items': list(self.get_photos()),
        }

    def fetch_html(self):
        url = f'https://instagram.com/{self.username}'

        session = HTMLSession()
        response = session.get(url)

        if response.status_code == 200:
            response.html.render()
            return response.html

    def get_author_block(self):
        return {
            'name': self.username,
            'avatar': self.get_avatar_url(),
            'home_page_url': self.get_homepage_url(),
        }

    def get_title(self):
        return self.html.find('title')[0].text.split(')')[0] + ')'

    def get_homepage_url(self):
        return f'https://instagram.com/{self.username}'

    def get_avatar_url(self):
        meta = self.html.find('meta')
        for m in meta:
            if m.attrs.get('property') == 'og:image':
                return m.attrs['content']

    def get_photos(self):
        photos = [a for a in self.html.find('a') if a.attrs['href'].startswith('/p/')]

        for photo in photos:
            post_id = 'https://instagram.com' + photo.attrs['href']
            author = post_id.split('taken-by=')[-1]
            photo_img = photo.find('img')[0]
            content_text = photo_img.attrs.get('alt', '')
            image = photo_img.attrs['src']

            yield {
                'id': post_id,
                'url': post_id,
                'content_text': content_text,
                'image': image,
                'author': author,
            }


def main(username):
    feed = InstagramFeed(username)
    print(json.dumps(feed.generate(), indent=2))


if __name__ == '__main__':
    main(sys.argv[-1])
