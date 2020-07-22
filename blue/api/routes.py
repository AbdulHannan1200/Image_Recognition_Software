from flask import Blueprint,jsonify, request
from flask_restful import Api,Resource
import pandas as pd
from werkzeug.utils import secure_filename
import sys 
import os
import json
import h5py
from tensorflow.keras.models import load_model
import requests
from PIL import Image
import urllib
import numpy as np
from flask_sqlalchemy import SQLAlchemy
import bcrypt

dirname = os.path.dirname(os.path.abspath(__file__))
dirname_list = dirname.split("\\")[:-1]
dirname = "\\".join(dirname_list)
print(dirname)
path = dirname + "\\api"
print(path)
sys.path.append(path)



path02 = dirname + "\\api\\Models"

sys.path.append(path02)

mod = Blueprint('api',__name__)
api = Api(mod)

db = SQLAlchemy()


from data_upload import Upload_Data
from TrainingModel import Model_Train
from TrainingModel import Delete_Data
from model_prediction import Prediction_Func

class Create_Project(Resource):
    def post(self):
        try:
            proj_path = dirname + "\\Projects"

            postedData=request.get_json()
        
            proj_name=postedData['project_name']
            first_category=postedData['category_one']
            second_category=postedData['category_two']

            name_and_path = proj_path + "\\" + proj_name
            path01 = name_and_path + "\\" + first_category
            path02 = name_and_path + "\\" + second_category
        
            if not os.path.exists(name_and_path):
            
                
                if not os.path.exists(path01):
                    
                    if not os.path.exists(path02):
                        os.mkdir(name_and_path)
                        print("created project : ", proj_name)
                        os.mkdir(path01)
                        os.mkdir(path02)
                        print("created categories : ", first_category,second_category)
                
                        ret={"status":200,"msg":"Successfully created project"}         
                        return jsonify(ret)

                else:
                    print(proj_name, " folder already exists.")
                    ret={"status":401,"msg":"category with this name already exist"}         
                    
                    return jsonify(ret)
        
                ret={"status":200,"msg":"Successfully created project"}         
                return jsonify(ret)

            else:
                print(proj_name, " folder already exists.")
                ret={"status":401,"msg":"Project with this name already exist"}         
                
                return jsonify(ret)
  
        except Exception as e:
            ret={"status":401,"msg":"Cannot create this project","Problem":e}         
            return jsonify(ret)


class Uploading_Data(Resource):
    def post(self):
        try:
            proj_path = dirname + "\\Projects"

            postedData=request.get_json()
        
            proj_name=postedData['project_name']
            category=postedData['category']
            urls=postedData['urls']
        

            project_path = proj_path + "\\" + proj_name
            cat_path = project_path + "\\" + category

            if os.path.exists(project_path):
                if os.path.exists(cat_path):

                    for url in urls:
                        retJson = Upload_Data(cat_path,url)
                    return jsonify({"status":200,"msg":retJson})

                else:
                    retJson = {"status":404,"msg":"Category with this name doesn't exist"}
                    return jsonify(retJson)

            else:
                retJson = {"status":404,"msg":"Project with this name doesn't exist"}
                return jsonify(retJson)

        except Exception as e:
            ret={"status":401,"msg":"Cannot Upload","Problem":e}         
            return jsonify(ret)
        


class Train_Models(Resource):
    def post(self):
        try:

            proj_path = dirname + "\\Projects"
            postedData=request.get_json()
        
            proj_name=postedData['project_name']
            cat1 =postedData['category1']
            cat2 =postedData['category2']

            categories=[cat1,cat2]

            DIR_NAME = proj_path + "\\" + proj_name

            retJson = Model_Train(DIR_NAME,categories)

            Delete_Data(DIR_NAME,categories)


            return jsonify(retJson)
    
        except Exception as e:
            ret={"status":401,"msg":"Error in training model","Problem":e}         
            return jsonify(ret)


class Prediction(Resource):
    def post(self):
        try:

            postedData=request.get_json()
            url=postedData['url']
            proj_name=postedData['project_name']
            cat1 =postedData['category1']                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
            cat2 =postedData['category2']

            proj_path = dirname + "\\Projects"
            DIR_NAME = proj_path + "\\" + proj_name

            model_path = DIR_NAME + "\\" + "model.h5"

            model = load_model(model_path,compile=False)

            

            categories=[cat1,cat2]

            retJson = Prediction_Func(url,categories,model)
            
            return jsonify(retJson)
        
        except Exception as e:
            ret={"status":401,"msg":"Cannot use this image for prediction","Problem":e}         
            return jsonify(ret)


class Get_Projects(Resource):
    def get(self):
        try:
            proj_path = dirname + "\\Projects"
            
            complete_list = dict()
            proj_list = list()
            
            subfolders_projects = [ f.path for f in os.scandir(proj_path) if f.is_dir() ]
          
            for proj in subfolders_projects:
                cat_list = list()
                last_name = proj.split("\\")
                last_name = last_name[-1]
       
                proj_list.append(last_name)


                projects_categories = [ f.path for f in os.scandir(proj) if f.is_dir() ]
                for cate in projects_categories:
                    print(cate)
                    cat_last_name = cate.split("\\")
                    cat_last_name = cat_last_name[-1]
                    print(cat_last_name)

                    cat_list.append(cat_last_name)
                    
                
                complete_list[last_name] = cat_list


            retJson = {"status":200,"projects":proj_list,"categories":complete_list}
            
            return jsonify(retJson)

        except Exception as e:
            ret={"status":401,"msg":"Cannot find projects","Problem":e}         
            return jsonify(ret)

class Get_Projects_Without_Data(Resource):
    def get(self):
        try:
            proj_path = dirname + "\\Projects"

            complete_list = dict()
      
            subfolders_projects = [ f.path for f in os.scandir(proj_path) if f.is_dir() ]
       
         
            cat_count = 0
            for proj in subfolders_projects:
  
                cat_list = list()
                last_name = proj.split("\\")
                last_name = last_name[-1]
       
                projects_categories = [ f.path for f in os.scandir(proj) if f.is_dir() ]
                for cate in projects_categories:
                   
                    cat_last_name = cate.split("\\")
                    cat_last_name = cat_last_name[-1]
                   
                    cat_list.append(cat_last_name)
                   
                    extensions = [".jpg", ".jpeg", ".png"]
                    filelist = [ f for f in os.listdir(cate) if os.path.splitext(f)[1] in extensions]

                    print(filelist)

                    if len(filelist) <= 0:
                        cat_count += 1

                        if cat_count > 1:
                            complete_list[last_name] = cat_list
                            print("1st",complete_list)
                            
                        elif cat_count == 1 :
                            print("here")
                            print(cat_last_name)
                            print(complete_list)
                            complete_list[last_name] = cat_last_name
                            print("2nd",complete_list)

                   

            print("3rd",complete_list)
            retJson = {"status":200,"missing_data_projects":complete_list,"NumberOfMissingCategories":cat_count}
            
            return jsonify(retJson)
        except Exception as e:
            ret={"status":401,"msg":"Cannot find projects","Problem":e}         
            return jsonify(ret)



class Users (db.Model) :
    id = db.Column(db.Integer , primary_key=True)
    user_name = db.Column(db.String(40))
    password = db.Column(db.String(20))
    user_email=db.Column(db.String(40))


def UserExist(username,email):
  
        s = db.session()
        query = s.query(Users).filter(Users.user_email==email) 
        query1=s.query(Users).filter(Users.user_name==username) 
        result = query.first()
        result2=query1.first()
        print(result2)
        print(result)
        if result==None and result2==None:
            return False
        else:
            return True




class Sign_Up(Resource):
    def post(self):

        postedDate=request.get_json()
        name = postedDate['user_name']
        password = postedDate['password']
        email=postedDate["user_email"]
        #yhn pe chala ky dekh lyna same pe dera hai ture ya false pe

        if UserExist(name,email):
            retJson = {"status" : 301, "msg": "already register"}

        

        #Store username and pw into the database
        else:
            hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
            user1 = Users(user_name= name,password = hashed_pw,user_email=email)
            db.session.add(user1)
            db.session.commit()
            retJson = {"status":200,"msg":"singup successfully"}
        return jsonify(retJson)

def verify_user(email,password):
    s = db.session()
    query = s.query(Users).filter(Users.user_email==email)
    result = query.first()
    if result == None:
        return False,None
   
    else:
        print("password",password)
        #hashed_pw=bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        for name,db_password in s.query(Users.user_name,Users.password).filter(Users.user_email==email):
            print(name)
            print(db_password)
            
            if bcrypt.hashpw(password.encode('utf8'), db_password) == db_password:
                return True,name
            else:
                return False,None
    


class Login(Resource):
    def post(self):
        postedDate=request.get_json()

        email = postedDate['user_email']
        password = postedDate['password']
        result,name=verify_user(email,password)

        if  result== False:
            retJson = {"status" : 301, "msg": "Invalid Username or Password"}
            return jsonify(retJson)

        else:
            retJson = {"status":200,"msg":"You've successfully signed up to the Api","User Name":name}
            return jsonify(retJson)




api.add_resource(Create_Project, "/create_project")
api.add_resource(Uploading_Data, "/upload_data")
api.add_resource(Train_Models, "/train")
api.add_resource(Prediction, "/predict")
api.add_resource(Get_Projects, "/get_Projects")
api.add_resource(Get_Projects_Without_Data, "/get_empty_Projects")
api.add_resource(Sign_Up, '/sign_up')  
api.add_resource(Login, '/login')