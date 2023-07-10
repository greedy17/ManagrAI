import CryptoJS from 'crypto-js'

export function encryptData(data, key) {
  const encrypted = CryptoJS.AES.encrypt(JSON.stringify(data), key)
  return encrypted.toString()
}

export function decryptData(encryptedData, key) {
  const decrypted = CryptoJS.AES.decrypt(encryptedData, key)
  if (decrypted.toString(CryptoJS.enc.Utf8).trim()) {
    return JSON.parse(decrypted.toString(CryptoJS.enc.Utf8))
  } else return {}
}