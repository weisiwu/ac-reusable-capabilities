import {uiScenes} from './scenes-ui.mjs';
import {systemScenes} from './scenes-system.mjs';

export const sceneRenderers = Object.freeze({...uiScenes, ...systemScenes});
