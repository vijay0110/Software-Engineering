# Testing Plan

## Authentication Tests

### User Registration

1. Valid Registration
* Input: Email: "a@example.com", Nickname: "a", Password: "a"
* Expected Result: User is registered successfully and redirected to login page

2. Invalid Registration

* Missing Email
    * Input: Email: "", Nickname: "testuser", Password: "password123"
    * Expected Result: Flash message "Email is required."

* Missing Nickname
    * Input: Email: "test@example.com", Nickname: "", Password: "password123"
    * Expected Result: Flash message "Nickname is required."

* Missing Password
    * Input: Email: "test@example.com", Nickname: "testuser", Password: ""
    * Expected Result: Flash message "Password is required."

* Invalid Email Format
    * Input: Email: "invalidemail", Nickname: "testuser", Password: "password123"
    * Expected Result: Flash message "Email Address format is incorrect."

* Existing Nickname
    * Input: Email: "testuser@gmail.com", Nickname: "testuser", Password: "password123"
    * Expected Result: Flash message "The choosen email address or nickname is already registered."

### User Login

1. Valid Login

* Input: Username: "testuser", Password: "abcd"
* Expected Result: User is logged in, session contains user_id and empty jokesVisited list

2. Invalid Login

* Missing Username
    * Input: Username: "", Password: "test"
    * Expected Result: Flash message "Email or Nickname is required."
* Missing Password
    * Input: Username: "a", Password: ""
    * Expected Result: Flash message "Password is required."
* Incorrect Password
    * Input: Username: "testuser", Password: "a"
    * Expected Result: Flash message "Incorrect password."
* Incorrect Username
    * Input: Username: "testuser12", Password: "abcd"
    * Expected Result: Flash message "Incorrect username."

## Joke Functionality Tests

1. Create Joke

* Valid Joke Creation
    * Input: Title: "Test Joke", Body: "This is a test joke"
    * Expected Result: Joke is created, user's joke balance increases by 1

* Invalid Joke Creation
    * Title Too Long
        * Input: Title: "A " * 11, Body: "This is a test joke"
        * Expected Result: Flash message "Title contains more than 10 words."
    * Duplicate Title
        * Input: Title: "Duplicate Joke", Body: "Another test joke" (after creating a joke with the same title)
        * Expected Result: Flash message "Title of Joke must be unique."

2. View My Jokes
* Input: User creates a joke with title "My Joke"
* Expected Result: "My Joke" appears on the my_jokes page

3. Update Joke
* Input: Change body of "Update Joke" to "Updated body"
* Expected Result: Joke body is updated in the database

4. Delete Joke
* Input: Delete joke with title "Delete Joke"
* Expected Result: Joke is removed from the database

5. View Joke
* Input: View joke with title "A Test Joke"
* Expected Result: Page displays "A Test Joke" and "A Test Joke Body"

6. Joke Balance
* Input: Create a new joke
* Expected Result: User's joke balance increases by 1

## Moderator Functionality Tests

1. Moderator Home Access
* Input: Moderator accesses /mod/home
* Expected Result: Page displays "Moderator Action Page"

2. Non-Moderator Home Access
* Input: Regular user accesses /mod/home
* Expected Result: User is redirected

3. Manage Moderators
* Input: Moderator accesses /mod/manage_moderators
* Expected Result: Page displays "Moderators List"

4. Add Moderator
* Input: Add user with id 1 as moderator
* Expected Result: User's is_mod field is set to 1 in the database

5. Delete Moderator
* Input: Delete moderator with id 2
* Expected Result: User is removed from the database

6. Manage User Balances
* Input: Moderator accesses /mod/manage_user_balances
* Expected Result: Page displays "User's joke balance"

7. Update User Balance
* Input: Set user 1's joke balance to 10
* Expected Result: User's joke_balance is updated to 10 in the database

8. Manage Jokes
* Input: Moderator accesses /mod/manage_jokes
* Expected Result: Page displays "Joke List"

9. Manage Logging
* Input: Moderator accesses /mod/manage_logging
* Expected Result: Page displays "Enable/Disable debug"

10. Toggle Debug Logging
* Input: Moderator toggles debug logging
* Expected Result: App logger's FileHandler level is set to DEBUG

11. Unauthorized Access
* Input: Unauthenticated user accesses /mod/home
* Expected Result: User is redirected

12. Database Error Handling
* Input: Drop user table and access /mod/manage_moderators
* Expected Result: User is redirected due to database error

## Database Tests

1. Get and Close Database
* Input: Access database within app context and execute a query after closing
* Expected Result: Database connection is established and closed properly, raising a sqlite3.ProgrammingError when trying to execute a query on a closed connection