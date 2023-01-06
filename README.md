# Picky Picky #

----------

This app allows users to create profiles based on their own food likes and dislikes, their preferred (or required) diets, and/or their potential food intolerances. These profiles are then used to deliver recipes based on their profiles.


----------

## Features ##



- Users are given the opportunity to create "child" profiles that can deliver recipes based on that "child" profile's settings.

- Users are able to follow other users.
 
- Users are able to share recipes with their followers based on their followers list. Recipients of those shares can reply to the original user.

- Users are able to save, review, and rate "favorite" recipes. These favorites are displayed on a user's profile  so that following users can see their favorited recipes and read their reviews.


----------

Recipe summaries, pictures, and assorted info are supplied by [https://spoonacular.com/food-api](https://spoonacular.com/food-api "Spoonacular Food API").


----------

## User Flow ##

- Users register for an account. Passwords are hashed via bcrypt. 

- Users can edit their information at any time via the "Edit Account" button on their user page. Users can also delete their account via the "Delete Account" button on the same page.

- Users at that point have the ability to see the general user page, follow users, receive shared recipes, and reply to shares.

- To find recipes, users must create a user profile. Users can input disliked foods ("No thank you foods"), liked foods ("Yes please foods"), select a diet via a pulldown menu, as well as input any food intolerances. No fields are required, obviously any inputs will be used to narrow down a search.

- Users can then search for recipes via the 'Get Recipes Now" button. They are directed to a page where 25 recipes are provided at random based on their inputs, which are put into a query to the api. Clicking on the name of the recipe brings users to a recipe page that provides a picture, a recipe summary, and assorted information about the recipe. The recipe page is also where users can share or favorite a recipe.

- The "Share Recipe" button brings users to a form where they can select a recipient of their share via a pulldown menu of their followers. They can also rate the recipe as well as send a short message. These messages will then show up on the recipients user page. Following users cannot see another user's messages.

- The "Favorite Recipe" button brings users to a form where they can save the recipe to a favorite list, give a short review of the recipe, and rate it between 1 and 5. Favorited recipes will show up on the user's user page. Following users can see favorited recipes on a user's page.

- To create a Child Profile, a user must have already created their own user profile. From there, a 'Create Child Profile' button will appear. Clicking on the 'Create Child Profile' button brings users to a form similar to the form to create a user profile. User flow from there is the same.

- Received shares are displayed on a user's page. Shares show a picture of the shared recipe, the recipe name, a html link to the recipe page, the name of the sharing user, and a message (if any). A "Reply" button is also displayed.

- The "Reply" button brings the user to a form where a short reply can be sent to the original sending user. Replies are displayed on the reply recipient's user page. Only the user can see their received shares and replies.

