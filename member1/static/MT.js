const explainBlocks = document.querySelectorAll('.explain');
console.log(explainBlocks);
const explainObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('show');
    }
  });
}, {
  threshold: 0.3
});
console.log("Starting observe");

explainBlocks.forEach(el => explainObserver.observe(el));
console.log("Finished observe");