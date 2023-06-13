import requests
from bs4 import BeautifulSoup


def main():
    url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('main').find('header').find('h1')
    title_text = title_tag.text
    post_image_url = soup.find('img', class_='attachment-post-image')['src']
    post_content = soup.find('main').find('div', class_='entry-content')
    post_text = post_content.text
    print(title_text)
    print(post_image_url)
    print(post_text)


if __name__ == '__main__':
    main()
