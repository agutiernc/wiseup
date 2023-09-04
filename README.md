# WiseUp - A conversation starter app

## Demo
http://wiseupapp.herokuapp.com

username: `demouser`

password: `1Demouser#`

*Note:* A delay may occur when logging in as the database is initializing.

## Project API
Leveraging Reddit's API, WiseUp targets *TodayILearned* and *Jokes* subreddits to provide a seamless way to access knowledge and humor. Employing OAuth 2.0 for secure authentication and data retrieval.

https://www.reddit.com/dev/api

## Description
**WiseUp** is your conversation companion, designed to assist those who struggle to find the right words and break the ice when engaging in conversations.

## User Flow
When you visit **WiseUp**, you'll be greeted with five random topics sourced from the *TodayILearned* and *Jokes* subreddits on reddit.com. Each topic comes with a handy link for further information. The top comment is also included from the Reddit post, which can be both informative and amusing. This dynamic duo of topic and comment is your conversational icebreaker toolkit.

To keep track of your favorite topics, simply click the star button next to their titles. You can revisit these favorites anytime by clicking on the "Favorites" tab.

But that's not all! **WiseUp** also serves up a daily dose of humor with the "Joke of the Day." Click on the joke to reveal the punchline, adding a touch of laughter to your conversations.

For any account-related actions, head over to the "User Settings" page. There, you can update your email, change your password, or even bid farewell and delete your account.

We're here to make your experience smooth and user-friendly!

## Technology Stack
The following were used to create **WiseUp**:
  - Python
  - JQuery
  - Flask
  - SQLAlchemy
  - WTForms
  - Jinja2
  - PostgreSQL
  - Axios
  - BCrypt
  - Bootstrap
  - Heroku