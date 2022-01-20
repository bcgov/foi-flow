import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import MinistriesCanvassed from './MinistriesCanvassed';

describe('<MinistriesCanvassed />', () => {
  test('it should mount', () => {
    render(<MinistriesCanvassed />);
    
    const ministriesCanvassed = screen.getByTestId('MinistriesCanvassed');

    expect(ministriesCanvassed).toBeInTheDocument();
  });
});