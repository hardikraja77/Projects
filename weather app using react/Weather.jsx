import search from './assets/search.png';
import sunny from './assets/sunny.jpeg';
import rainy from './assets/rainy.jpeg';
import cloudy from './assets/cloudy.jpeg';
import drizzle from './assets/drizzle.jpeg';
import city from './assets/city.jpeg';
import './Weather.css'
import { useState,useEffect } from 'react';

const Weatherdetail = ({icon,temp,loc,lat,lon,coun,hum,wind})=>{
    return(
        <>
        <div>
            <img src={icon} alt="sunny" className='img1'></img>
        </div>
        <div className='temp'>{temp}</div>
        <div className='loc'>{loc}</div>
        <div className='coun'>{coun}</div>
        <div className='cord'>
        <div className='lat'>
            <span>Latitude</span>
            <span>{lat}</span>
        </div>
        <div className='lon'>
            <span>Longitude</span>
            <span>{lon}</span>
        </div>
        </div>
        <div className='humwind'>
        <div className='hum'>Humidity : {hum}</div>
        <div className='wind'>Wind Speed : {wind}</div>
        </div>
        </>
    );
};



export const Weather= () =>{
    const [icon,setIcon] = useState(sunny);
    const [temp,setTemp] = useState(0);
    const [loc,setLoc] = useState("tirunelveli");
    const [coun,setCoun] = useState("");
    const [lat,setLat] = useState(0);
    const [lon,setLon] = useState(0);
    const [hum,setHum] = useState(0);
    const [wind,setWind] = useState(0);
    const [load,setLoad] = useState(false);
    const [citynotfound,setcitynotfound] = useState(false);

    const weather_details = {
        "01d":sunny,
        "01n":sunny,
        "02d":cloudy,
        "02n":cloudy,
        "03d":sunny,
        "03n":sunny,
        "04d":cloudy,
        "04n":cloudy,
        "09d":drizzle,
        "09n":drizzle,
        "10d":rainy,
        "10n":rainy,
        "13d":sunny,
        "13n":sunny,
        "50d":cloudy,
        "50n":cloudy,


    }
    useEffect(function(){
        weather_api();
    },[]);
    

    const key = "b1c8743c5f45f64e2f019f1690bd7a24";

    const weather_api = async () =>{
        setLoad(true);
        var url = `https://api.openweathermap.org/data/2.5/weather?q=${loc}&appid=${key}&units=Metric`;
        try{
            let res = await fetch(url);
            let res_json = await res.json();
            console.log(res_json);
            if(res_json.cod === "404"){
                setcitynotfound(true);
                return;
            }
            setTemp(res_json.main.temp);
            setHum(res_json.main.humidity);
            setWind(res_json.wind.speed);
            setLat(res_json.coord.lat);
            setLon(res_json.coord.lon);
            const code = res_json.weather[0].icon;
            setIcon(weather_details[code]);
            setcitynotfound(false);

        }catch{
            console.error("error : ",console.error);
    

        }finally{
            setLoad(false);

        }
    }

    const search1 = (e)=>{
        setLoc(e.target.value);    
    }

    const handlekey =(e)=>{
        if(e.key === "Enter"){
            weather_api();
        }
    }


    
    return(
        <>
        <div className='outer-container'>
            <div className='inner-container'>
                <input placeholder="Search City"  onChange={search1} className='inp' onKeyDown={handlekey} value={loc}></input>
                <img src={search} alt="search" className='img' onClick={weather_api}/>
            </div>
            {!citynotfound && <Weatherdetail icon={icon} temp={temp} loc={loc} lat={lat} lon={lon} coun={coun} hum={hum} wind={wind}/>}
            {citynotfound && <div>
                <img src={city} alt="city" className='city'></img>
                <div className='cnf'>City Not found...</div>
            </div>}
                
        </div>
        </>
    )
}