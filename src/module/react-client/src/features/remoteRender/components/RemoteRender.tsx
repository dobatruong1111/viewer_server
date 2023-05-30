import React, { FC, useCallback, useEffect, useRef } from 'react';
import vtkRemoteView from 'vtk.js/Sources/Rendering/Misc/RemoteView';

import { useWSLink } from '../hooks/useWSLink';
import protocols from '../lib/protocols';

import styles from './RemoteRender.module.css';

export const RemoteRender = () => {
  const { client, busy } = useWSLink({ protocols });

  if (client && !busy) return <RemoteRenderDisplay client={client} />;

  return <div>LOADING</div>;
};

type RemoteRenderDisplayProps = {
  client: unknown;
};
const RemoteRenderDisplay: FC<RemoteRenderDisplayProps> = (props) => {
  const { client } = props;
  const elementRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef({});

  const connect = useCallback(() => {
    const session = client.getConnection()?.getSession();
    const view = viewRef.current;
    if (view && session) {
      view.setSession(session);
      view.setViewId('-1');
      view.render();
    }
  }, [client]);

  useEffect(() => {
    if (elementRef.current) {
      const view = vtkRemoteView.newInstance({
        rpcWheelEvent: 'viewport.mouse.zoom.wheel', // RPC call
      });
      viewRef.current = view;
      // default of 0.5 causes 2x size labels on high-DPI screens. 1 good for demo, not for production.
      if (location.hostname.split('.')[0] === 'localhost') {
        view.setInteractiveRatio(1);
      }
      // initialize connection
      view.setContainer(elementRef.current);
      window.addEventListener('resize', view.resize);

      connect();
    }

    return () => {
      // if (this.subscription) {
      //   this.subscription.unsubscribe();
      //   this.subscription = null;
      // }
      window.removeEventListener('resize', viewRef.current.resize);
      // viewRef.current.delete();
    };
  }, [connect]);

  return <div className={styles['remote-render']} ref={elementRef}></div>;
};
