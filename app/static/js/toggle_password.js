function togglePassword(id, btn) {
    const input = document.getElementById(id);
    const isPassword = input.type === "password";

    input.type = isPassword ? "text" : "password";

    btn.innerHTML = isPassword
        ? `
      <svg xmlns="http://www.w3.org/2000/svg" class="icon-eye-off" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.269-2.943-9.543-7a10.025 10.025 0 012.092-3.368M6.343 6.343A9.956 9.956 0 0112 5c4.478 0 8.269 2.943 9.543 7a9.956 9.956 0 01-4.132 5.132M15 12a3 3 0 01-3 3m0-6a3 3 0 013 3m-3 3a3 3 0 01-3-3m6 0a3 3 0 00-3-3m0 0a3 3 0 00-3 3m0 0L3 3m18 18l-2-2"/>
      </svg>`
        : `
      <svg xmlns="http://www.w3.org/2000/svg" class="icon-eye" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
      </svg>`;
}