# from flask_login import UserMixin
# from . import db, login_manager

# @login_manager.user_loader
# def load_user(user_id):
#     return User.objects(username=user_id).first()

# class User(db.Document, UserMixin):
#     username = db.StringField(unique=True, required=True, min_length=4, max_length=20)
#     email = db.EmailField(unique=True, required=True)
#     password = db.StringField(required=True)
#     logs = db.ListField(db.ReferenceField('Log'))
    
#     def get_id(self):
#         return self.username
    
#     def __repr__(self):
#         return f"<User {self.username}>"