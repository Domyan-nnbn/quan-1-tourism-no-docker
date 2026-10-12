// Credentials are supplied by the build environment, never committed here.
module.exports = ({config}) => {
  const api = (process.env.EXPO_PUBLIC_API_URL || '').trim();
  const release = ['preview', 'production'].includes(process.env.EAS_BUILD_PROFILE);
  if (release) {
    let url;
    try { url = new URL(api); } catch { throw new Error('Set EXPO_PUBLIC_API_URL to your public HTTPS API origin before building.'); }
    if (url.protocol !== 'https:' || url.username || url.password || url.search || url.hash || url.pathname !== '/') {
      throw new Error('EXPO_PUBLIC_API_URL must be an HTTPS origin without credentials, path or query.');
    }
  }
  return {
    ...config,
    plugins: config.plugins || [],
  };
};
