//function that gets the location and returns it
function getLocation() {
    if(navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
      } else {
        console.log("Geo Location not supported by browser");
      }
}
//function that retrieves the position
function showPosition(position) {
    var location = {
        longitude: position.coords.longitude,
        latitude: position.coords.latitude
    }
    console.log(location)
}

//request for location
getLocation();

