/**
 * @jest-environment jsdom
 */

// Import the function to test. Ensure that your comments.js file exports toggleReplies.
// For example, if you refactored your file to use module.exports = { toggleReplies, ... }
import { toggleReplies } from '../static/js/comments';

describe('toggleReplies', () => {
  let toggleContainer, toggleButton, repliesContainer;

  beforeEach(() => {
    // Create a DOM structure similar to what your template produces:
    // <div class="my-comment-toggle">
    //   <button class="btn btn-link toggle-replies">Hide Replies</button>
    // </div>
    // <div class="replies" style="display: block;"></div>
    toggleContainer = document.createElement('div');
    toggleContainer.className = 'my-comment-toggle';

    toggleButton = document.createElement('button');
    toggleButton.className = 'btn btn-link toggle-replies';
    toggleButton.textContent = 'Hide Replies';
    toggleContainer.appendChild(toggleButton);

    repliesContainer = document.createElement('div');
    repliesContainer.className = 'replies';
    repliesContainer.style.display = 'block';

    // Append the toggle container and replies container to the document body
    document.body.appendChild(toggleContainer);
    document.body.appendChild(repliesContainer);
  });

  afterEach(() => {
    // Clean up the DOM
    document.body.innerHTML = '';
  });

  test('should hide replies when toggle is clicked if replies are visible', () => {
    // Initially, repliesContainer is "block" and toggleButton text is "Hide Replies"
    toggleReplies(toggleButton);

    expect(repliesContainer.style.display).toBe('none');
    expect(toggleButton.textContent).toBe('Show More Replies');
  });

  test('should show replies when toggle is clicked if replies are hidden', () => {
    // First, hide the container manually
    repliesContainer.style.display = 'none';
    toggleButton.textContent = 'Show More Replies';

    toggleReplies(toggleButton);

    expect(repliesContainer.style.display).toBe('block');
    expect(toggleButton.textContent).toBe('Hide Replies');
  });
});
