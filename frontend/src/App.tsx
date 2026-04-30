import { BrowserRouter } from "react-router-dom";

import { AppRoutes } from "./routes/AppRoutes";

/**
 * アプリケーションのルートコンポーネント。
 *
 * React Routerを設定し、画面遷移を有効にする。
 */
function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;