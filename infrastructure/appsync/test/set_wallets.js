var ApolloClient = require("@apollo/client").ApolloClient;
var InMemoryCache = require("@apollo/client").InMemoryCache;
var createHttpLink = require("@apollo/client").createHttpLink;
var createAuthLink = require("aws-appsync-auth-link").createAuthLink;
var gql = require("@apollo/client").gql;

var fetch = require('cross-fetch/polyfill');
const { Token } = require("graphql");

//token needs to be updated to run
const token = "eyJraWQiOiIwUldMeEprQ041UE5LQmljMmhIaWN5TWhIXC9JVmVDQmFBbmNDbTNCXC96TlU9IiwiYWxnIjoiUlMyNTYifQ.eyJhdF9oYXNoIjoib1BUQTlVZk9yMnkxUDZ0T2c0V3c3ZyIsInN1YiI6IjJjZDQwMDkyLWVhNjYtNDk3ZC1iOTA2LWFmZjMzOTRmZjIzYSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9vRGhvdU5pMkIiLCJjb2duaXRvOnVzZXJuYW1lIjoiYXNkZiIsImF1ZCI6IjNwbmk1OTdodGhuZWJxMjFic3ZwdmkydHFpIiwiZXZlbnRfaWQiOiI4YTEzNzI0Yy1mZGNiLTQwZDctYWM0OS1kMDM2NDBlYTNlMmMiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTY0OTk1NjYxNCwiZXhwIjoxNjQ5OTYwMjE0LCJpYXQiOjE2NDk5NTY2MTQsImp0aSI6Ijc3NjNmOGM5LTI3M2YtNDdkZi04MDU4LWUzMmQ1YTUwMzhhNiIsImVtYWlsIjoiYnJlbmRlbi5qdWRzb25AZ21haWwuY29tIn0.l1Ow_CMfaxcoaPo8s6zBfev2bZ_VSi8oBoSrJhC43RMP6nOUMhG4AdcKfC5DDRn3U6HfeE76jSN3ZbTCOYul1z5XwXzKvuRFihRGKdyoP_7KzdXVdW6FaPXutU6qcbMMknyXJ-Q6rDfKHGj-zPoD5-2Ei83n3gXNnMblnkbvcbpGY4jwJtRyt8QyMBCsp2FAfqijEc2Mt6dMAam5EOMHAa1_p_3023c7u90nYc3zZqnQZuJEwNf9g82Ipids3ZvUQMmPVlOkKHAbp9tkWacIFvPGiT1Ce_BkNjkhtUuddsBEshLC6JE4ImipNAgyibphhQHmo5sbt-6hwFbgsniyew"
username = 'asdf'
const URL = "https://tntqao5pj5eblmhvww7nd4byne.appsync-api.us-east-1.amazonaws.com/graphql"

async function getToken(){
    return token
}

const httpLink = createHttpLink({
    uri: URL,
});

const authLink = createAuthLink({
    url: URL,
    region: 'us-east-1',
    auth: {
        type: 'AMAZON_COGNITO_USER_POOLS',
        jwtToken: () => getToken()
    }
})

const client = new ApolloClient({
    fetch,
    link: authLink.concat(httpLink),
    cache: new InMemoryCache()
});



client
  .mutate({
    mutation: gql`
        mutation SetWallet {
            updateUser(username: "${username}", wallets: "testtest") {
            wallets
            }
        }
    `
  })
  .then(result => console.log(result));


