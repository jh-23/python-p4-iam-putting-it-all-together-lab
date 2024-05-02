#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    
    def post(self):
        
        json = request.get_json()
        user = User(
            username=json.get('username'),
            image_url=json.get('image_url'),
            bio=json.get('bio')
        )
        user.password_hash = json['password']


        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(), 201
        except IntegrityError:
            return {'message': 'invalid username, password, image URL or bio'}, 422
        
class CheckSession(Resource):
    
    def get(self):
        
        user = User.query.filter(User.id == session['user_id']).first()
        
        if user:
            response = make_response(
                user.to_dict(),
                200
            )
        else:
            response = make_response(
                {'message': 'error'},
                401,
            )
        return response

class Login(Resource):
    
    def post(self):
        username = request.get_json()['username']
        user = User.query.filter(User.username == username).first()
        
        password = request.get_json()['password']
        
        if user:
            if user.authenticate(password):
                session['user_id'] = user.id
            return user.to_dict()
        
        else:
            return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    
    def delete(self):
        if session['user_id'] != None:
            session['user_id'] = None
            return {}, 204
        elif session['user_id'] == None:
            return {'error': 'message'}, 401
    
    
class RecipeIndex(Resource):
    
    def get(self):
        
        user = User.query.filter(User.id == session['user_id']).first()
        
        recipes = Recipe.query.all()
        
        

        if user:
            recipe_list = [recipe.to_dict() for recipe in user.recipes]
            return recipe_list, 200
        else:
            return {'error': '401'}, 401

    
    def post(self):
        json = request.get_json()
            
        # if session['user_id'] is not None:
        # user = User.query.filter(User.id == session['user_id']).first()
            
        try:
                
            recipe = Recipe(user_id=session['user_id'],
                            title=json['title'],
                            instructions=json['instructions'],
                            minutes_to_complete=json['minutes_to_complete']
                            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except IntegrityError:
                return {'error': '422: Unprocessable Entity'}, 422
        
        # else:
            # return {'message': 'error'}, 401


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)