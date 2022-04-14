var ApolloClient = require("@apollo/client").ApolloClient;
var InMemoryCache = require("@apollo/client").InMemoryCache;
var createHttpLink = require("@apollo/client").createHttpLink;
var createAuthLink = require("aws-appsync-auth-link").createAuthLink;
var gql = require("@apollo/client").gql;

var fetch = require('cross-fetch/polyfill');
const { Token } = require("graphql");

//token needs to be updated to run
const token = "eyJraWQiOiIwUldMeEprQ041UE5LQmljMmhIaWN5TWhIXC9JVmVDQmFBbmNDbTNCXC96TlU9IiwiYWxnIjoiUlMyNTYifQ.eyJhdF9oYXNoIjoiLTk5MzN4WE9ualBpb2t0N3ROZWdzZyIsInN1YiI6IjJjZDQwMDkyLWVhNjYtNDk3ZC1iOTA2LWFmZjMzOTRmZjIzYSIsImF1ZCI6IjNwbmk1OTdodGhuZWJxMjFic3ZwdmkydHFpIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjQ5OTUxMjcxLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9vRGhvdU5pMkIiLCJjb2duaXRvOnVzZXJuYW1lIjoiYXNkZiIsImV4cCI6MTY0OTk1NDg3MSwiaWF0IjoxNjQ5OTUxMjcxLCJqdGkiOiI3MmY5YWMxMS1hZGE5LTRmNzctYWNjMC1jYmI0NjEzZjJkNTUiLCJlbWFpbCI6ImJyZW5kZW4uanVkc29uQGdtYWlsLmNvbSJ9.D0xRNusnqmzNEgqn_XtWgNywUpzyi6Qov2ohEm3mwt6GINBT6gVCmbJW5d8sos-gji3qlHNMQ-ycWhb8a_lrDxlqXNE8G65FJfHr5wg6pEoKE2LTOzz-CGK2c59dqWorOxm_F0t8jZJONZRGmMGeozPqUonaHxPTsMqVQjXJRc93yedndTXCfAv0TA-2UliRxloB0va_oa1ZUlkd-YR15cLXTA4xo8jLWJTHuPTiimT7TaeDW2jZJf1nsoZw5gqjSXsWPZRwYXhqAzGhYhrQ9OTB8ma7sQ_V3at07_xfP5s-6k9YR2aSbE2iirBI0obZJoR3E4FAKQkpoYjpPtSGEg"
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
  .query({
    query: gql`
        query MyQuery {
            getUsers {
                username
            }
        }
    `
  })
  .then(result => console.log(result.data.getUsers));


