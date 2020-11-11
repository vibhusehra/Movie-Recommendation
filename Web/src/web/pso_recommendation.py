import numpy as np 
import pandas as pd
from web.models import Myrating
import random

gbest = None

class Particle:
    
    def __init__(self, user_dims, movie_dims):
        
        self.error = float('inf')
        
        ####### USERS #######

        self.curr_user = np.random.random(user_dims) #(610,k)
        self.per_best_user = self.curr_user
        self.velocity_user = np.random.random(user_dims)
        

        ####### MOVIES #######
        self.curr_movie = np.random.random(movie_dims) #(9724,k)
        self.per_best_movie = self.curr_movie
        self.velocity_movie = np.random.random(movie_dims)
        

        
        
        
        
    def __str__(self):
        return "My error is {err}".format(err = self.error)
    
    
    def move(self):
        self.curr_user += self.velocity_user
        self.curr_movie += self.velocity_movie
        
        
def RMSE(prediction, target):
    return np.sqrt(np.mean((prediction-target)**2))


def PSO(iterations, population, c1, c2, result, latent_features):
    
    particles = []
    
    user_dims = (result.shape[0], latent_features)
    movie_dims = (result.shape[1], latent_features)
    print("userDims: ",user_dims)
    print("movie_dims: ",movie_dims)

    for i in range(population):
        particles.append(Particle(user_dims,movie_dims))
    
    error_min = 0.000001
    i = 0
    error = float("inf")
    gbest = Particle(user_dims,movie_dims)

    pred_matrix = None
    # number of epochs
    while i < iterations and gbest.error > error_min:
        
        for particle in particles:

            particle_res = np.dot(particle.curr_user, particle.curr_movie.T)

            
            # error
            particle_error = RMSE(particle_res, result)
            if particle_error < particle.error:
                particle.per_best_user = particle.curr_user
                particle.per_best_movie = particle.curr_movie
                particle.error = particle_error
                
            if particle_error < gbest.error:
                
                gbest = particle
                pred_matrix = particle_res

                
                
        for particle in particles:
            particle.velocity_user = 0.02*particle.velocity_user + c1*random.random()*(particle.per_best_user - particle.curr_user) + c2*random.random()*(gbest.per_best_user - particle.curr_user)
            particle.velocity_movie = 0.02*particle.velocity_movie + c1*random.random()*(particle.per_best_movie - particle.curr_movie) + c2*random.random()*(gbest.per_best_movie - particle.curr_movie)
            particle.move()
                
            
        print('epoch: {ep}, error {gbest}'.format(ep=i,gbest=gbest.error))
        i += 1
    return (gbest, pred_matrix)
    
    

def find_movie(user_rating, pred_matrix):

    t=[]
    q=sorted(range(pred_matrix.shape[1]), key=lambda k: pred_matrix[-1,k])
    q.reverse()
    for j in q:
        if(user_rating[-1,j]==0):
            t.append(j)
    return(t)


def recommendation(n, recommendations):
    i=0
    movie_data=pd.read_csv('data/movies.csv')
    while(n > 0):
        # print(l[user][i],"    ",movie_data["title"][l[user][i]])
        print(recommendations[i],"    ",movie_data["title"][recommendations[i]])
        i += 1
        n -= 1



def recommendMovie(user):
    '''
        - user ratings
        - load user ratings
        - add user ratings to the user rating table
    '''
    user_ratings = np.load('data/user_ratings.npy')
    # print((Myrating.objects.all().values()))
    indiv_ratings = Myrating.objects.filter(user=user).values()
    print(indiv_ratings)
    
    # create curr user rating array (user_ratings.shape[1]) --> zero array
    curr_user_ratings = np.zeros(user_ratings.shape[1])

    # entries bharo in the curr user --> ratings ajaygi
    for dic in indiv_ratings:
        curr_user_ratings[dic['movie_id'] - 1] = dic['rating']

    # print(curr_user_ratings[:30])
    # append this to user_ratings
    user_ratings = np.vstack((user_ratings,curr_user_ratings))
    print(user_ratings.shape)


    gbest, pred_matrix = PSO(1,100,2,5,user_ratings,latent_features=3)
    # print(pred_matrix[-1][:30])

    # recommend
    recommendation(10, find_movie(user_ratings, pred_matrix))




