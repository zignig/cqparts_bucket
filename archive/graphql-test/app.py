#!/usr/bin/python
from flask import Flask
from graphene import ObjectType, String, Schema
from flask_graphql import GraphQLView


class Query(ObjectType):
    hello = String(description="Hello")

    def resolve_hello(self, args, context, info):
        return "World"


view_func = GraphQLView.as_view("graphql", graphiql=True, schema=Schema(query=Query))

app = Flask(__name__)
app.add_url_rule("/graphql", view_func=view_func)


if __name__ == "__main__":
    app.run(debug=True)
