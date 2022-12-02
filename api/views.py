from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet,ViewSet
from rest_framework.response import Response
from rest_framework import permissions,authentication


from api.serializers import ProductsSerializer,CartSerializer,ReviewSerializer
from api.models import Products,Carts,Reviews
from rest_framework.decorators import action
from rest_framework import serializers

# Create your views here.

class ProductsView(ModelViewSet):
    serializer_class=ProductsSerializer
    queryset=Products.objects.all()
    permission_classes=[permissions.IsAuthenticated]
    #authentication_classes=[authentication.TokenAuthentication]
                  
    @action(methods=["GET"],detail=False)
    def categories(self,request,*args,**kw):
        qs=Products.objects.values_list("category",flat=True).distinct()
        return Response(data=qs)

        
    def list(self,request,*args,**kw):
        qs=Products.objects.all()
        if "category" in request.query_params:
            qs=qs.filter(category=request.query_params.get("category"))
        serializer=ProductsSerializer(qs,many=True)
        return Response(data=serializer.data)

    @action(methods=["POST"],detail=True)
    def addto_cart(self,request,*args,**kw):
        product=self.get_object()
        user=request.user
        serializer=CartSerializer(data=request.data,context={"user":user,"product":product})
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)
            
    @action(methods=["post"],detail=True)
    def add_review(self,request,*args,**kw):
        Product=self.get_object()
        user=request.user
        serializer=ReviewSerializer(data=request.data,context={"user":user,"product":Product})
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)            

class CartsView(ViewSet):
   # authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def list(self,request,*args,**kw):
        qs=Carts.objects.filter(user=request.user)
        serializer=CartSerializer(qs,many=True)
        return Response(data=serializer.data)

    
    def destroy(self,request,*args,**kw):
        id=kw.get("pk")
        object=Carts.objects.get(id=id)
        if object.user==request.user:
            object.delete()
            return Response(data="deleted")
        else:
          raise serializers.ValidationError("you have no permision to perform this operation")


from rest_framework import mixins
from rest_framework import generics
from api.models import Reviews

class ReviewDeleteView(mixins.DestroyModelMixin,generics.GenericAPIView):
    serializer_class=ReviewSerializer
    queryset=Reviews.objects.all()
    def delete(self,request,*args,**kw):
        id=kw.get("pk")
        review=Reviews.objects.get(id=id)
        if review.user==request.user:
            return self.destroy(request,*args,**kw)
        else:
            raise serializers.ValidationError("you have no permission")    
        