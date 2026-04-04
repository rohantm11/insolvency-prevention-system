import React from 'react';
import { Composition } from 'remotion';
import { SolvencyVideo } from './SolvencyVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="SolvencyInsight"
      component={SolvencyVideo}
      durationInFrames={630}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
