from flask import Blueprint, render_template, url_for, flash, redirect, send_from_directory, request, current_app
from flask_login import login_required, current_user
import os
from .. import forms, db
from ..models import User, Property, PropertyFavourites, PropertyImages
from datetime import datetime
import requests
import re
import base64

properties_views = Blueprint('properties_views', __name__)


@properties_views.route("/map", methods=['GET', 'POST'])
@login_required
def map_page():
    result_list, property_list = [], []
    target_address = []
    form = forms.TargetLocationForm()
    dynamic_form = forms.DynamicForm()
    filters_form = forms.FiltersForm()
    target = [1.369635, 103.803680]  # middle of sg coords
    if form.validate_on_submit():
        target_location = form.target_location.data
        url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=N&getAddrDetails=Y&pageNum=1".format(
            target_location  # 639798
        )
        response = requests.request("GET", url)
        data = response.json()
        pages = data['totalNumPages']

        for item in data['results']:
            result_list.append((item['ADDRESS'], item['ADDRESS']))
        # print(result_list)

        for i in range(2, pages + 1):
            url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=N&getAddrDetails=Y&pageNum={}".format(
                target_location,
                i
            )
            response = requests.request("GET", url)
            data = response.json()
            for item in data['results']:
                result_list.append((item['ADDRESS'], item['ADDRESS']))

        dynamic_form.address.choices = result_list

        return render_template("query_map_page.html", user=current_user, form=form, result_list=result_list,p_list = [],
                               dynamic_form=dynamic_form, filters_form = filters_form,property_list=[],
                               target=target, target_address = [])

    elif dynamic_form.validate_on_submit() and not filters_form.validate_on_submit():
        target_location = dynamic_form.address.data
        filters_form.address.data = target_location
        url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            target_location
        )
        response = requests.request("GET", url)
        data = response.json()
        #data['results'] may be empty
        if (len(data['results']) == 0):
            # Show an alert with the error message and navigate back
            error_message = "Invalid address, please select another address."
            return f"<script>alert('{error_message}'); history.go(-1);</script>"

        address_details = data['results'][0]
        target_address = address_details
        # print(address_details)

        # query into db for properties
        initial_property_list = Property.query_(float(address_details['LATITUDE']), float(address_details['LONGITUDE']), [])
        # print(f"initial list {initial_property_list}")
        # print(f"length is {len(property_list)}")
        # print(property_list[0]['distance'])
        filtered = list(filter(lambda num: num['distance'] < 10 # testing at 10
                               and num['monthly_rent'] < 10000,
                               initial_property_list))  #default filters, distance 0-3km, monthly_rent 0-10000sgd
        # print(len(filtered))
        # print(filtered)
        return render_template("query_map_page.html", user=current_user, form=form, result_list=result_list,p_list = initial_property_list,
                               dynamic_form=dynamic_form,filters_form = filters_form, property_list=filtered,
                               target=[float(address_details['LATITUDE']), float(address_details['LONGITUDE'])],target_address = target_address)
    elif filters_form.validate_on_submit():
        
        address = filters_form.address.data
        distance_min = filters_form.distance_min.data
        distance_max = filters_form.distance_max.data
        monthly_rent_max = filters_form.monthly_rent_max.data
        floor_size_min = filters_form.floor_size_min.data
        floor_size_max = filters_form.floor_size_max.data
        num_of_bedrooms_min = filters_form.num_of_bedrooms_min.data
        num_of_bedrooms_max = filters_form.num_of_bedrooms_max.data
        ppsm_min = filters_form.ppsm_min.data
        ppsm_max = filters_form.ppsm_max.data
        year_built_min = filters_form.year_built_min.data
        year_built_max = filters_form.year_built_max.data
        floor_level_min = filters_form.floor_level_min.data
        floor_level_max = filters_form.floor_level_max.data
        furnish_status = filters_form.furnish_status.data
        lease_term = filters_form.lease_term.data
        negotiable = filters_form.negotiable.data
        flat_type = filters_form.flat_type.data
        gender = filters_form.gender.data


        url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            address
        )
        response = requests.request("GET", url)
        data = response.json()
        address_details = data['results'][0]
        target_address = address_details
        # print(address_details)

        # query into db for properties
        initial_property_list = Property.query_(float(address_details['LATITUDE']), float(address_details['LONGITUDE']), [])
        # print(len(property_list))
        # print(property_list[0]['distance'])
        filtered = list(filter(lambda num: num['distance'] > distance_min
                               and num['distance'] < distance_max
                               and num['monthly_rent'] < monthly_rent_max
                               and num['number_of_bedrooms'] > num_of_bedrooms_min
                               and num['number_of_bedrooms'] < num_of_bedrooms_max
                               and num['floorsize'] > floor_size_min
                               and num['floorsize'] < floor_size_max
                               and num['price_per_square_metre'] > ppsm_min
                               and num['price_per_square_metre'] < ppsm_max
                               and num['year_built'] > year_built_min
                               and num['year_built'] < year_built_max
                               and num['floor_level'] > floor_level_min
                               and num['floor_level'] < floor_level_max
                               and num['furnishing'] == furnish_status
                               and num['lease_term'] == lease_term
                               and num['negotiable_pricing'] == negotiable
                               and num['flat_type'] == flat_type
                               and num['gender'] in gender,

                               initial_property_list))  #default filters, distance 0-3km, monthly_rent 0-10000sgd
        


        return render_template("query_map_page.html", user=current_user, form=form, result_list=result_list,
                               dynamic_form=dynamic_form, filters_form = filters_form,property_list=filtered,target_address = target_address,
                               target=[float(address_details['LATITUDE']), float(address_details['LONGITUDE'])])

    return render_template("query_map_page.html", user=current_user, form=form, result_list=result_list,
                           dynamic_form=dynamic_form, filters_form = filters_form,property_list=property_list,
                           target=target,target_address = target_address)


@properties_views.route("/map/<int:property_id>", methods=['GET', 'POST'])
@login_required
def map_page_info(property_id=None):
    property = Property.query.filter_by(property_id=property_id).first()
    if property is None or property.is_visible == 0 or property.is_approved == 0:
        flash("Property not found", category="error")
        return redirect(url_for("properties_views.map_page"))
    else:
        form = forms.TargetLocationForm()
        target_coord = []
        route_data = {}
        target_location = ""
        map_urls = []
        # if redirected from map page, fill in form automatically 
        args = request.args
        if args.get("t_coords") and args.get("t_address") and re.match(r'^\d+\.\d+\,\d+\.\d+$', args.get("t_coords")): # check if valid args
            url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
                args.get("t_address").replace("-", " ")
            ) 
            response = requests.request("GET", url)
            data = response.json()
            form.target_location.data = data['results'][0]['ADDRESS'] # honestly, can just use address from args

        if form.validate_on_submit():
            # get target location details
            target_location = form.target_location.data
            url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
                target_location
            )
            response = requests.request("GET", url)
            target_data = response.json()
            
            if len(target_data['results']) == 0:
                flash("Invalid address, please select another address.", category="error")
                return redirect(url_for("properties_views.map_page_info", property_id=property_id))

            # get route details
            target_coord = [target_data['results'][0]['LATITUDE'], target_data['results'][0]['LONGITUDE']]
            property_coord = [property.latitude, property.longitude]
            url = "https://www.onemap.gov.sg/api/public/routingsvc/route?start={p_lat}%2C{p_lng}&end={t_lat}%2C{t_lng}&routeType={routeType}&date={date}&time={hh}%3A{mm}%3A{ss}&mode={mode}&maxWalkDistance={walk_dist}&numItineraries={result}".format(
                p_lat=property_coord[0],
                p_lng=property_coord[1],
                t_lat=target_coord[0],
                t_lng=target_coord[1],
                routeType='pt', # pt, drive, walk
                date=datetime.today().strftime('%m-%d-%Y'),
                hh=datetime.now().strftime('%H'),
                mm=datetime.now().strftime('%M'),
                ss=datetime.now().strftime('%S'),
                mode='TRANSIT', # TRANSIT, BUS, RAIL, WALK
                walk_dist=500, # 500m
                result=3 # 1-3 results
            )
            headers = {"Authorization": current_app.config["ONE_MAP_TOKEN"]} # one map api key
            response = requests.request("GET", url, headers=headers)
            route_data = response.json()
            if response.status_code == 400:
                flash("No route found", category="error")
                print(route_data)
                route_data = {}

            elif response.status_code == 200:
                for iter in route_data['plan']['itineraries']:
                    map_url = "https://www.onemap.gov.sg/amm/amm.html?mapStyle=Default&zoomLevel=11"
                    # iwt (infowindow text) isnt working properly because the api is shit
                    # iwt messes up the routing lines on the map
                    # even without iwt, routing works half the time
                    for i in range(len(iter['legs'])):
                        leg = iter['legs'][i]
                        
                        # property location
                        if i == 0:
                            iwt = "%3Cp%3E" + property.block + "%20" + property.street_name.replace(" ","%20") + "%20" + property.building.replace(" ","%20") + "%3C%2Fp%3E"
                            iwt = base64.urlsafe_b64encode(iwt.encode("ascii")).decode("ascii")
                            map_url += "&marker=postalcode:{}!icon:fa-hotel!iwt:{}!colour:red!rType:{}!rDest:{},{}".format(property.postal,iwt,leg['mode'],leg['to']['lat'], leg['to']['lon'])
                            #map_url += "&marker=postalcode:{}!icon:fa-hotel!colour:red!rType:{}!rDest:{},{}".format(property.postal,leg['mode'],leg['to']['lat'], leg['to']['lon'])

                        # route transfers
                        else:
                            iwt = "%3Cp%3E" + leg['from']['name'].replace(" ","%20") + "%3C%2Fp%3E"
                            iwt = base64.urlsafe_b64encode(iwt.encode("ascii")).decode("ascii")
                            if leg['mode'] == 'WALK':
                                fa = "fa-user"
                            elif leg['mode'] == 'BUS':
                                fa = "fa-bus"
                            elif leg['mode'] == 'SUBWAY':
                                fa = "fa-subway"
                            map_url += "&marker=latLng:{},{}!icon:{}!iwt:{}!colour:red!rType:{}!rDest:{},{}".format(leg['from']['lat'], leg['from']['lon'],fa,iwt,leg['mode'],leg['to']['lat'], leg['to']['lon'])
                            #map_url += "&marker=latLng:{},{}!icon:{}!colour:red!rType:{}!rDest:{},{}".format(leg['from']['lat'], leg['from']['lon'],fa,leg['mode'],leg['to']['lat'], leg['to']['lon'])

                    # target location
                    iwt = "%3Cp%3E" + target_data['results'][0]['ADDRESS'].replace(" ","%20") + "%3C%2Fp%3E"
                    iwt = base64.urlsafe_b64encode(iwt.encode("ascii")).decode("ascii")
                    map_url += "&marker=postalcode:{}!icon:fa-star!iwt:{}!colour:red&popupWidth=200".format(target_data['results'][0]['POSTAL'],iwt)
                    #map_url += "&marker=postalcode:{}!icon:fa-star!colour:red&popupWidth=200".format(target_data['results'][0]['POSTAL'])
                    map_urls.append(map_url)
        
        landlord = User.query.filter_by(user_id=property.user_id).first()
        property_images = PropertyImages.query.filter_by(property_id=property_id).all()
        property_favourite = PropertyFavourites.query.filter_by(property_id=property_id).first()

        return render_template("property_page.html", user=current_user, property=property, 
                               property_images=property_images, property_favourite=property_favourite, 
                               landlord=landlord, form=form,route_data=route_data, target_location=re.sub("SINGAPORE\s\d+$","",target_location),map_urls=map_urls)
    
@properties_views.route("/map/<int:property_id>/favourite", methods=['POST'])
@login_required
def favourite_property(property_id=None):
    property = Property.query.filter_by(property_id=property_id).first()
    if property is None or property.is_visible == 0 or property.is_approved == 0:
        return {"error": "Property not found"}
    else:
        if PropertyFavourites.query.filter_by(user_id=current_user.user_id).count() >= 10:
            return {"error": "You have reached the maximum number of favourites"}

        property_favourite = PropertyFavourites.query.filter_by(property_id=property_id, user_id=current_user.user_id).first()
        if property_favourite is None:
            property_favourite = PropertyFavourites(property_id=property_id, user_id=current_user.user_id)
            db.session.add(property_favourite)
            db.session.commit()
            return {"message": "Property added to favourites"}
        else:
            db.session.delete(property_favourite)
            db.session.commit()
            return {"message": "Property removed from favourites"} 

@properties_views.route("/account/favourites", methods=['GET'])
@login_required
def favourited_properties():
    property_favourites = PropertyFavourites.query.filter_by(user_id=current_user.user_id).all()
    property_list = []
    property_images = []
    for property_favourite in property_favourites:
        property = Property.query.filter_by(property_id=property_favourite.property_id).first()
        if property is not None and property.is_visible == 1 and property.is_approved == 1:
            property_list.append(property)
            property_images.append(PropertyImages.query.filter_by(property_id=property.property_id).first())
    return render_template("favourite_properties_page.html", user=current_user, property_list=property_list, property_images=property_images)

@properties_views.route("/storage/<path:filename>")
def property_image_url(filename):
    path = (os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'website', 'storage', 'property_images'))
    return send_from_directory(path, filename)

