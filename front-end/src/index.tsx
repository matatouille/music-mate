import { UserProvider } from "./context/UserContext";
import { h, render } from "preact";
import { Router } from "preact-router";
import { Home, Messages, Profile, SignUp } from "./routes";
import { SWRConfig } from "swr";
import { fetcher } from "./config/api";

import "./style.css";

const App = () => {
  return (
    <div className="flex flex-col w-screen h-screen bg-gray-50">
      <UserProvider>
        <SWRConfig
          value={{
            fetcher: fetcher,
          }}
        >
          <Router>
            <Home path="/" />
            <Messages path="/messages/:guid" />
            <SignUp path="/signup" />
            <Profile path="/profile" isEditable={true} />
            <Profile path="/profile/:guid" isEditable={false} />
          </Router>
        </SWRConfig>
      </UserProvider>
    </div>
  );
};

render(<App />, document.body);
