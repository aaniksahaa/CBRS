import React, { useEffect, useState } from "react";

const LocationComponent = () => {
  const [location, setLocation] = useState({ latitude: null, longitude: null });
  const [error, setError] = useState(null);
  const [geoEnabled, setGeoEnabled] = useState(true);

  useEffect(() => {
    const checkGeolocation = () => {
      if (!navigator.geolocation) {
        setGeoEnabled(false);
        setError("Geolocation is not supported by this browser.");
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        (err) => {
          if (err.code === err.PERMISSION_DENIED) {
            setError(
              "Please enable location services in your browser settings."
            );
          } else {
            setError(err.message);
          }
        }
      );
    };

    checkGeolocation();
  }, []);

  return (
    <div>
      <h1>User Location</h1>
      {!geoEnabled && <p>{error}</p>}
      {geoEnabled && error ? (
        <p>Error: {error}</p>
      ) : (
        <p>
          Latitude: {location.latitude} <br />
          Longitude: {location.longitude}
        </p>
      )}
      {geoEnabled && !error && (
        <p>
          If you haven't enabled geolocation, please go to your browser settings
          and allow location access for this site.
        </p>
      )}
    </div>
  );
};

export default LocationComponent;
