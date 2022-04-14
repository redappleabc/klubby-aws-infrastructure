var ApolloClient = require("@apollo/client").ApolloClient;
var InMemoryCache = require("@apollo/client").InMemoryCache;
var createHttpLink = require("@apollo/client").createHttpLink;
var createAuthLink = require("aws-appsync-auth-link").createAuthLink;
var gql = require("@apollo/client").gql;

var fetch = require('cross-fetch/polyfill');
const { Token } = require("graphql");

//token needs to be updated to run
const token = ""
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


