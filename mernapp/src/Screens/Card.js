import React from 'react'
import {Link} from 'react-router-dom'
export default function () {
  return (
    <div>
        <div className="card mt-3" style={{ width: "18rem", maxHeight: "360px" }}>
        <img src="..." className="card-img-top" alt="..." />
        <div className="card-body">
          <h5 className="card-title fs-5">Card title</h5>
          <p className="card-text fs-5">Some quick example text.</p>
          <div className='container w-100'>
            <select className='m-2 h-10 bg-success rounded fs-5'>
              {Array.from(Array(6), (e, i) => (
                <option key={i + 1} value={i + 1}>{i + 1}</option>
              ))}
            </select>

            <select className='m-2 h-100 bg-success rounded fs-5'>
              <option>Half</option>
              <option>Full</option>
            </select>
            <div className='d-inline h-100 fs-5'>Total price</div>
          </div>
          <Link to="#" className="btn btn-primary fs-5">Go somewhere</Link>
        </div>
      </div>
    </div>
  )
}
