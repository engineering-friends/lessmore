window.addEventListener('load', () => {
  const helloWorldDiv = document.createElement('div');
  helloWorldDiv.textContent = 'Hello world';
  helloWorldDiv.style.position = 'fixed';
  helloWorldDiv.style.top = '10px';
  helloWorldDiv.style.right = '10px';
  helloWorldDiv.style.backgroundColor = 'white';
  helloWorldDiv.style.padding = '10px';
  helloWorldDiv.style.border = '1px solid black';
  helloWorldDiv.style.zIndex = '10000';
  document.body.appendChild(helloWorldDiv);
});
