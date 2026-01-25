import React from 'react'
import Home from './components/Home/Home'
import Navbar from './components/Navigation/Navbar'
import ProblemSt from './components/Home/ProblemSt'
import Power from './components/Home/Power'
import Why from './components/Home/Why'
export default function App() {
  return (
    <div>
      <Navbar/>
      <Home/>
      <ProblemSt/>
      <Power/>
      <Why/>
    </div>
  )
}
