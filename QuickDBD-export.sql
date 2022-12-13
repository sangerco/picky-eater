-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.

-- Modify this code to update the DB schema diagram.
-- To reset the sample schema, replace everything with
-- two dots ('..' - without quotes).

CREATE TABLE "User" (
    "id" int   NOT NULL,
    "username" string   NOT NULL,
    "first_name" string   NOT NULL,
    "last_name" string   NOT NULL,
    "email" string   NOT NULL,
    CONSTRAINT "pk_User" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "User_profile" (
    "id" int   NOT NULL,
    "user_id" int   NOT NULL,
    "no_food_0" string   NULL,
    "no_food_1" string   NULL,
    "no_food_2" string   NULL,
    "no_food_3" string   NULL,
    "no_food_4" string   NULL,
    "no_food_5" string   NULL,
    "yes_food_0" string   NULL,
    "yes_food_1" string   NULL,
    "yes_food_2" string   NULL,
    "yes_food_3" string   NULL,
    "yes_food_4" string   NULL,
    "yes_food_5" string   NULL,
    "diet" string   NULL,
    CONSTRAINT "pk_User_profile" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Child_profile" (
    "id" int   NOT NULL,
    "user_profile_id" int   NOT NULL,
    "no_food_0" string   NULL,
    "no_food_1" string   NULL,
    "no_food_2" string   NULL,
    "no_food_3" string   NULL,
    "no_food_4" string   NULL,
    "no_food_5" string   NULL,
    "yes_food_0" string   NULL,
    "yes_food_1" string   NULL,
    "yes_food_2" string   NULL,
    "yes_food_3" string   NULL,
    "yes_food_4" string   NULL,
    "yes_food_5" string   NULL,
    "diet" string   NULL,
    CONSTRAINT "pk_Child_profile" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Favorite_recipes" (
    "id" int   NOT NULL,
    "user_profile_id" int   NOT NULL,
    "api_recipe_id" int   NOT NULL,
    "review" text   NULL,
    CONSTRAINT "pk_Favorite_recipes" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Friends" (
    "id" int   NOT NULL,
    "friend_1_id" int   NOT NULL,
    "friend_2_id" int   NOT NULL,
    CONSTRAINT "pk_Friends" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Shopping_lists" (
    "id" int   NOT NULL,
    "user_profile_id" int   NOT NULL,
    "api_shopping_list_id" int   NOT NULL,
    "notes" text   NOT NULL,
    CONSTRAINT "pk_Shopping_lists" PRIMARY KEY (
        "id"
     )
);

ALTER TABLE "User_profile" ADD CONSTRAINT "fk_User_profile_user_id" FOREIGN KEY("user_id")
REFERENCES "User" ("id");

ALTER TABLE "Child_profile" ADD CONSTRAINT "fk_Child_profile_user_profile_id" FOREIGN KEY("user_profile_id")
REFERENCES "User_profile" ("id");

ALTER TABLE "Favorite_recipes" ADD CONSTRAINT "fk_Favorite_recipes_user_profile_id" FOREIGN KEY("user_profile_id")
REFERENCES "User_profile" ("id");

ALTER TABLE "Friends" ADD CONSTRAINT "fk_Friends_friend_1_id" FOREIGN KEY("friend_1_id")
REFERENCES "User" ("id");

ALTER TABLE "Friends" ADD CONSTRAINT "fk_Friends_friend_2_id" FOREIGN KEY("friend_2_id")
REFERENCES "User" ("id");

ALTER TABLE "Shopping_lists" ADD CONSTRAINT "fk_Shopping_lists_id" FOREIGN KEY("id")
REFERENCES "User_profile" ("id");

