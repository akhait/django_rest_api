# Simple Django REST API
Routes:

`/auth/` - obtain JWT token

`/auth/verify/` - verify JWT token

`/auth/refresh/` - refresh JWT token

`/articles/` - list of articles published by user

`/articles/<pk>/` - an article identified by `<pk>`

`/articles/<pk>/sentences/` - list of sentences in article identified by `<pk>`

`/articles/<pk>/sentences/<num>/` - sentence number `<num>` in article identified by `<pk>`
