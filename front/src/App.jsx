import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './views/Dashboard'
import Inspector from './views/Inspector'
import Upload from './views/Upload'
import UploadJourSpecial from './views/UploadJourSpecial'
import UploadStudent from './views/UploadStudent'
import Parcours from './views/Parcours'
import CoursesDashboard from './views/Courses'
import ModifyYearInformations from './views/ModifyYearInformations'

function App() {

  return (
    <React.Fragment>
      <Router>
        <Routes>
          <Route path="/inspector/" element={<Inspector />} />
          <Route path="/inspector/parcours" element={<Parcours />} />
          <Route path="/inspector/upload/course" element={<Upload />} />
          <Route path="/inspector/upload/specialday" element={<UploadJourSpecial />} />  
          <Route path="/inspector/upload/student" element={<UploadStudent />} />
          <Route path="/inspector/yearinformations" element={<ModifyYearInformations />} />
          <Route path="/inspector/courses" element={<CoursesDashboard />} />
          <Route path="*" element={<Dashboard />} />
        </Routes>
      </Router>
    </React.Fragment>
  )
}

export default App
