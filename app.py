import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def changeLoginStatus(state):
    st.session_state["login_status"] = state
    st.rerun()
    
def main():

    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    #check the config status
    if st.session_state["authentication_status"]:
        authenticator.logout('Logout', 'sidebar', key='unique_key')
        st.write(f'Welcome {st.session_state["name"]}')
        
        #Get the user ID... here it is just the index of the user
        userId = list(config['credentials']['usernames'].keys()).index(st.session_state['username'])

        st.title('Some content')

    elif st.session_state["authentication_status"] is None or st.session_state["authentication_status"] is False:

        #add a message to the main screen
        st.warning('Please enter your username and password')

        if "login_status" not in st.session_state or st.session_state["login_status"] == "login":
            #Add a login widget
            name, auth, user = authenticator.login('Login', 'sidebar')
            if auth:
                #There was a cookie and the user is logged in
                st.rerun()

            #Add a register button
            if st.sidebar.button("Create User"):
                #the user taps on the "register" button
                changeLoginStatus("register")

            if st.sidebar.button("Forgot Username"):
                changeLoginStatus("forgot_username")

            if st.sidebar.button("Forgot Password"):
                changeLoginStatus("forgot_password")
        elif st.session_state["login_status"] == "forgot_username":
            #The user forgot their username
            try:
                username_of_forgotten_username, email_of_forgotten_username = authenticator.forgot_username('Forgot username', location="sidebar")
                if username_of_forgotten_username:
                    st.success('Username to be sent securely')
                    changeLoginStatus("login")
                    #TODO: Username should be transferred to user securely
                else:
                    st.error('Email not found')
            except Exception as e:
                st.error(e)

            if st.sidebar.button("Back To Login"):
                changeLoginStatus("login")
        elif st.session_state["login_status"] == "forgot_password":
            #The user forgot their password
            try:
                username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password('Forgot password', location="sidebar")
                if username_of_forgotten_password:
                    st.success('New password to be sent securely')
                    changeLoginStatus("login")
                    #TODO: Random password should be transferred to user securely
                else:
                    st.error('Username not found')
            except Exception as e:
                st.error(e)

            if st.sidebar.button("Back To Login"):
                changeLoginStatus("login")
        else:
            #the user tried to register
            try:
                #popup the register user widget
                if authenticator.register_user('Register user', location="sidebar", preauthorization=False):
                    st.success('User registered successfully')
                    st.session_state["login_status"] = "login"
    
                    #write out the user configuration
                    with open('./config.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)

                    st.rerun()
            except Exception as e:
                st.error(e)

            if st.sidebar.button("Back To Login"):
                changeLoginStatus("login")

        if st.session_state["authentication_status"] is False:
            #tell the user their username/pwd is wrong
            st.error('Username/password is incorrect')
            
    #if st.session_state["authentication_status"]:
    #    try:
    #        if authenticator.reset_password(st.session_state["username"], 'Reset password'):
    #            st.success('Password modified successfully')
    #    except Exception as e:
    #        st.error(e)

    #if st.session_state["authentication_status"]:
    #    try:
    #        if authenticator.update_user_details(st.session_state["username"], 'Update user details'):
    #            st.success('Entries updated successfully')
    #    except Exception as e:
    #        st.error(e)

if __name__ == "__main__":
    main()