# Home Assistant Ingress Solution

## The Problem

Kiwix generates HTML with absolute paths like `/skin/kiwix.css`. When accessed via Home Assistant ingress at `https://domain.com/api/hassio_ingress/<token>/wiki/`, the browser interprets these absolute paths as `https://domain.com/skin/kiwix.css` (site root), which returns 404.

## Why JavaScript Approach Failed

Previous attempts used client-side JavaScript to rewrite paths, but:
- Resources are requested BEFORE JavaScript executes
- The HTML parser starts fetching CSS/JS immediately upon encountering tags
- Interceptors installed after page load are too late
- `sub_filter` with placeholders + JS was hacky and unreliable

## The Clean Solution: nginx + Lua

### What Changed (v1.4.0)

1. **Added nginx-mod-http-lua**: Enables server-side Lua scripting in nginx
2. **Dynamic HTML Rewriting**: HTML is modified BEFORE reaching the browser
3. **Removed all JavaScript hacks**: No more client-side manipulation

### How It Works

```nginx
body_filter_by_lua_block {
    local ingress_prefix = ngx.var.ingress_prefix  -- e.g., "/api/hassio_ingress/TOKEN"
    local content_type = ngx.header.content_type or ""
    
    if string.match(content_type, "text/html") then
        local chunk = ngx.arg[1]
        if chunk then
            -- Rewrite: href="/skin/..." -> href="/api/hassio_ingress/TOKEN/skin/..."
            chunk = string.gsub(chunk, 'href="(/[^"]*)"', 'href="' .. ingress_prefix .. '%1"')
            chunk = string.gsub(chunk, 'src="(/[^"]*)"', 'src="' .. ingress_prefix .. '%1"')
            ngx.arg[1] = chunk
        end
    end
}
```

### Benefits

✅ **Server-side**: HTML modified before browser sees it
✅ **Variable support**: Can use dynamic ingress tokens  
✅ **Clean**: No client-side hacks or workarounds
✅ **Maintainable**: Standard nginx + Lua approach
✅ **Fast**: Single-pass modification at proxy layer
✅ **Reliable**: Works for all resources, not just XHR/fetch

### Implementation Details

**Building Lua Modules from Source**:
- nginx-mod-http-lua is not available in Home Assistant base images
- Solution: Compile modules during Docker build
- Downloads ngx_devel_kit and lua-nginx-module from GitHub
- Builds as dynamic modules matching container's nginx version
- Installed to `/usr/lib/nginx/modules/`
- Build dependencies cleaned up after compilation

**Trade-offs**:
- Slightly longer build time (~2-3 minutes for compilation)
- Adds ~5MB to image size for LuaJIT runtime
- Small CPU overhead for Lua pattern matching (negligible)
- **Benefit**: Clean, deterministic solution with no conditional code

## Testing

1. Rebuild the add-on (version 1.5.0+)
2. Access via ingress: Click add-on in Home Assistant sidebar
3. Open DevTools Network tab
4. Verify assets load from `/api/hassio_ingress/<token>/skin/...` paths
5. Check that Kiwix displays with proper CSS and functionality
6. Test navigation, search, and content viewing
7. Verify direct access (`http://IP:8111/`) also works correctly

## Why This Is The Right Approach

**Industry Standard**: nginx + Lua (or OpenResty) is a proven solution for dynamic reverse proxy modifications, used by major companies like Cloudflare, Kong API Gateway, and many CDN providers.

**No Browser Dependency**: Works regardless of browser, JavaScript settings, or client-side errors.

**Separation of Concerns**: Path rewriting is a proxy concern, not a client concern.

