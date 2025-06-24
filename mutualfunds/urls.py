from django.urls import path
from .views import  FetchAndSaveSchemesView, SchemeListView, PortfolioListCreateView, FetchAndSaveFundHousesView,\
    RegisterView
    
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('schemes/<int:fund_house_id>/', SchemeListView.as_view()),
    path('portfolio/', PortfolioListCreateView.as_view()),
    path('fundhouses/', FetchAndSaveFundHousesView.as_view(), name='fundhouses'),
    path('fetch-schemes/', FetchAndSaveSchemesView.as_view(), name='fetch-schemes'),

]
