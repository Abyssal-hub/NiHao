# iOS Installation Guide

There is **no `.ipa` file in the GitHub Releases** — Apple requires macOS + Xcode
to build and sign iOS apps, which cannot run on our Linux build server.
Three real ways to get NiHao on an iPhone:

---

## Option 1 — PWA (recommended, 30 seconds, free)

The app is already a full Progressive Web App: offline support, home-screen
icon, fullscreen, identical features to native.

1. Open **Safari** on your iPhone
2. Go to **https://abyssal-hub.github.io/NiHao/**
3. Tap the **Share** button (square with arrow ↑)
4. Scroll down → **"Add to Home Screen"** → Add
5. The 你 icon appears on your home screen like a native app

Works offline, updates automatically when online.

---

## Option 2 — Build the native app on any Mac (free Apple ID, 15 min)

The Capacitor iOS project is committed in this repo (`web/ios/`).

```bash
git clone https://github.com/Abyssal-hub/NiHao.git
cd NiHao/web
npm install
npx cap sync ios
open ios/App/App.xcworkspace        # opens Xcode (install from App Store if needed)
```

In Xcode:
1. Select the **App** target → **Signing & Capabilities**
2. Set **Team** to your Apple ID (free account works for personal use)
3. Connect your iPhone → select it as the run target → press **▶ Run**

This installs a signed app on your device (free signing lasts 7 days,
re-sign by rebuilding; paid Apple Developer $99/yr removes the limit and
enables App Store distribution).

---

## Option 3 — GitHub Actions macOS runner (CI build)

If you have an Apple Developer account, a workflow can build `.ipa`
artifacts on GitHub's `macos-latest` runners using your signing
certificates stored as repository secrets. Ask the maintainer to set this
up if needed — it requires your Apple credentials and cannot be done
without them.
