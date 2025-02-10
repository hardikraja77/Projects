import React from "react";
import { BrowserRouter as Router,Routes,Route } from "react-router-dom";
import Log  from "./Log";
import Home from "./Home";
import { Createdatabase } from "./Createdatabase";
import { Createtable } from "./Createtable";
import { Deletedatabase } from "./Deletedatabase";
import { Deletetable } from "./Deletetable";
import { Joins } from "./Joins";
import { Insert } from "./Insert"

const Routes1 = ()=>{
    return(
        <Router>
            <Routes>
                <Route path="/" element={<Log />} />
                <Route path="/home" element={<Home />} />
                <Route path="/create" element={<Createdatabase />} />
                <Route path="/createtable" element={<Createtable />} />
                <Route path="/deletedatabase" element={<Deletedatabase />} />
                <Route path="/deletetable" element={<Deletetable />} />
                <Route path="/joins" element={<Joins />} />
                <Route path="/insert" element={<Insert />} />
            </Routes>
        </Router>
    )
}

export default Routes1;