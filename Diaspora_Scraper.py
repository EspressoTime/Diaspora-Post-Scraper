import requests, bs4, time, calendar
session = requests.session()
username = ''
password = ''


def main():
    if username == '' or password == '':
        print('Error: Username or password is missing :(')
        return
    login()
    stream_data()


def login():
    # Log in to Diaspora
    login_url = 'https://joindiaspora.com/users/sign_in'
    # Extract CSRF token from login page
    r1 = session.get(login_url)
    login_soup = bs4.BeautifulSoup(r1.text, 'html.parser')  # Get login page contents
    token_tag = login_soup.select('meta[name="csrf-token"]')[0]  # Get meta tag with CSRF token
    token = token_tag['content']

    # Post login data
    values = {
        'user[username]': username,
        'user[password]': password,
        'authenticity_token': token
    }
    session.post(login_url, data=values) 
    print('Login successful.')


def stream_data():
    # Get JSON post data
    header_values = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    stream_content_url = 'https://joindiaspora.com/stream?_=' + str(time.time())  # Create stream content URL with current timestamp
    post_data = session.get(stream_content_url, headers=header_values).json()  # Get JSON post data
    last_post = post_data[-1]

    # Fetch first set of posts
    post_activity = {}
    authors = {}
    for ea in post_data:
        # Post activity count
        activity_count = int(ea['interactions']['comments_count']) + int(ea['interactions']['likes_count']) + int(ea['interactions']['reshares_count'])
        post_activity[ea['title']] = activity_count
        # Author count
        if ea['author']['name'] in authors:
            authors[ea['author']['name']] += 1
        else:
            authors[ea['author']['name']] = 1
    print('Retrieved first set of stream posts.')
    print('Total posts retrieved: ' + str(len(post_activity)))

    # Continue until 100 posts
    while len(post_activity) < 100:
        # Fetch new JSON sets by decreasing max time in URL to time of the last fetched post
        last_time = last_post['created_at']
        unix_time = calendar.timegm(time.strptime(str(last_time), '%Y-%m-%dT%H:%M:%S.000Z'))  # Example time: 2017-09-20T17:00:07.000Z
        next_page_url = 'https://joindiaspora.com/stream?max_time=' + str(int(unix_time)) + '&_=' + str(int(time.time()))
        new_post_data = session.get(next_page_url, headers=header_values).json()  # Get new JSON post data

        # If adding next set would total more than 100 posts, remove the last posts from the new set 
        if len(post_activity) + len(new_post_data) > 100:
            remove_count = len(post_activity) + len(new_post_data) - 100
            new_post_data = new_post_data[:-remove_count or None]

        for ea in new_post_data:
            # Post activity count
            activity_count = int(ea['interactions']['comments_count']) + int(ea['interactions']['likes_count']) + int(ea['interactions']['reshares_count'])
            post_activity[ea['title']] = activity_count
            # Author count
            if ea['author']['name'] in authors:
                authors[ea['author']['name']] += 1
            else:
                authors[ea['author']['name']] = 1
        print('Total posts retrieved: ' + str(len(post_activity)))
        last_post = new_post_data[-1]

    active_post = max(post_activity, key=post_activity.get)
    print('\nMost active post: "' + active_post + '", ' + str(post_activity[active_post]) + ' interactions')
    active_user = max(authors, key=authors.get)
    print('Most active user: "' + active_user + '", ' + str(authors[active_user]) + ' posts')

main()
