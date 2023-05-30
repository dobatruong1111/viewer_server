import { useEffect, useState } from 'react';
import vtkWSLinkClient from 'vtk.js/Sources/IO/Core/WSLinkClient';
import { connectImageStream } from 'vtk.js/Sources/Rendering/Misc/RemoteView';
import SmartConnect from 'wslink/src/SmartConnect';

const config = {
  application: 'Cone',
  sessionURL: `ws://${location.hostname}:1234/ws`,
};

// Bind vtkWSLinkClient to our SmartConnect
vtkWSLinkClient.setSmartConnectClass(SmartConnect);

/**
 * Handle initialization logic for consumers of WSLink
 * Returns a client object as well as busy status
 * @return {object} client
 * @return {boolean} busy
 */
export const useWSLink = ({ protocols }) => {
  const [busy, setBusy] = useState();
  const [client, setClient] = useState<
    ReturnType<(typeof vtkWSLinkClient)['newInstance']> | undefined
  >();

  useEffect(() => {
    let newClient: typeof client;
    if (!client) {
      newClient = vtkWSLinkClient.newInstance({ protocols });
      newClient.onBusyChange((count) => {
        setBusy(count);
      }, 1);
      newClient.beginBusy();
      // Error
      newClient.onConnectionError((httpReq) => {
        const message =
          (httpReq && httpReq.response && httpReq.response.error) || `Connection error`;
        console.error(message);
        console.log(httpReq);
      });

      // Close
      newClient.onConnectionClose((httpReq) => {
        const message =
          (httpReq && httpReq.response && httpReq.response.error) || `Connection close`;
        console.error(message);
        console.log(httpReq);
      });

      // Connect
      newClient
        .connect(config)
        .then((validClient) => {
          connectImageStream(validClient.getConnection().getSession());
          setClient(validClient);
          newClient?.endBusy();
          console.log('client remote', validClient.getRemote());
          // Now that the client is ready let's setup the server for us
          validClient
            .getRemote()
            [config.application].createVisualization()
            .catch(console.error);
        })
        .catch((error) => {
          console.error(error);
        });
    }
    return () => {
      if (newClient) {
        // newClient.disconnect();
      }
    };
  }, [client, protocols]);
  return { client, busy };
};
