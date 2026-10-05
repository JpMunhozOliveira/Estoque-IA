document.querySelectorAll("input.reais").forEach(el => {
  const formatar = () => {
    let d = el.value.replace(/\D/g, "").replace(/^0+/, "").padStart(3, "0");
    const inteiro = d.slice(0, -2).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    el.value = inteiro + "," + d.slice(-2);
  };
  el.addEventListener("input", formatar);
  formatar();
});