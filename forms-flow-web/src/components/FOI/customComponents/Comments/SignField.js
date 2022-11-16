import React, { useContext } from 'react'
import './comments.scss'
import { ActionContext } from './ActionContext'

const SignField = () => {
  const actions = useContext(ActionContext)

  const handleDivClick = (e) => {
    if (e.target.name === 'login') {
      window.location.href = actions.signinUrl
    } else if (e.target.name === 'signup') {
      window.location.href = actions.signupUrl
    }
  }

  return (
    <div className="signBox">
      <div className="signLine">
        Log in or sign up to leave a comment
      </div>
      <div>
        <button
          className="loginBtn"
          name='login'
          onClick={(e) => handleDivClick(e)}
        >
          Log In
        </button>
        <button
          className="signBtn"
          name='signup'
          onClick={(e) => handleDivClick(e)}
        >
          Sign Up
        </button>
      </div>
    </div>
  )
}

export default SignField
