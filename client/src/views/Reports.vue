<template>
  <div class="reports">
    <div v-if="creating">
      <div class="chat-window">
        <div class="chat-window__header">
          <p>Coverage Report</p>
        </div>

        <div ref="chatWindow" class="chat-window__body">
          <div class="space-between">
            <div></div>
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/profile.svg" height="12px" alt="" />
              <p>Help me create a coverage report</p>
            </div>
          </div>

          <div>
            <div class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="brandText"></p>
              </div>
            </div>
          </div>

          <div v-if="brand" class="space-between">
            <div></div>
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/profile.svg" height="12px" alt="" />
              <p>{{ brand }}</p>
            </div>
          </div>

          <div v-if="brand">
            <div style="width: fit-content" class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="uploadText"></p>
              </div>

              <div style="margin: 0 0 8px 14px" class="row">
                <div class="file-input-wrapper">
                  <label class="file-input-label">
                    <input type="file" @change="uploadImage" class="file-input" />
                    <span style="margin-right: 4px" class="secondary-button">
                      <img
                        v-if="loading"
                        style="margin-right: 4px"
                        class="invert rotation"
                        src="@/assets/images/loading.svg"
                        height="14px"
                        alt=""
                      />
                      Upload Logo
                    </span>
                  </label>
                  <p style="margin-left: 8px" class="file-name">
                    {{ fileName ? fileName : 'No file selected' }}
                  </p>

                  <img
                    v-if="fileName"
                    style="margin-left: 8px"
                    :src="uploadedImageUrl"
                    height="40px"
                    alt=""
                  />
                </div>
              </div>
            </div>
          </div>

          <div v-if="fileName" class="space-between">
            <div></div>
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/profile.svg" height="12px" alt="" />
              <p>{{ fileName }} uploaded</p>
            </div>
          </div>

          <div v-if="fileName">
            <div style="width: 80%" class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="fileText"></p>
              </div>

              <div style="margin: 0 0 8px 14px">
                <p class="thin-font">Paste up to 1,000 URLs. Each on a new line.</p>
                <textarea
                  style="
                    width: 100%;
                    border: 1px solid rgba(0, 0, 0, 0.1) !important;
                    padding: 12px;
                  "
                  :rows="5"
                  id="search-input"
                  class="area-input"
                  autocomplete="off"
                  :placeholder="urlPlaceholder"
                  v-model="reportUrls"
                  v-autoresize
                  :disabled="urlsSet"
                />
                <div style="margin-top: 12px" class="flex-end">
                  <button
                    @click="setUrls"
                    :disabled="!reportUrls || urlsSet"
                    class="primary-button"
                  >
                    Continue
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="urlsSet" class="space-between">
            <div></div>
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/profile.svg" height="12px" alt="" />
              <p>Urls uploaded</p>
            </div>
          </div>

          <div v-if="urlsSet">
            <div class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="lastInstructions"></p>
              </div>

              <div style="margin: 0 0 8px 8px">
                <button class="primary-button">Run report</button>
              </div>
            </div>
          </div>
        </div>

        <div class="chat-window__footer">
          <div class="large-input-container">
            <div style="border-radius: 28px" class="input-container-gray">
              <section>
                <textarea
                  ref="textarea"
                  style="width: 100%"
                  :rows="1"
                  id="search-input"
                  class="area-input"
                  autocomplete="off"
                  placeholder="Message ManagrAI..."
                  v-model="searchText"
                  v-autoresize
                  :disabled="loading || !!brand"
                  @keyup.enter="generateReportSearch($event)"
                />

                <div
                  v-if="chatSearch"
                  @click="generateReportSearch($event)"
                  class="left-margin pointer lite-bg img-container-stay-alt"
                  style="margin-right: 12px"
                >
                  <img
                    style="margin: 0"
                    src="@/assets/images/paper-plane-full.svg"
                    height="10px"
                    alt=""
                  />
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else>testing here</div>
  </div>
</template>

<script>
export default {
  name: 'Reports',
  data() {
    return {
      creating: true,
      brandText: 'Using the message bar, tell us which brand this report is for',
      loading: false,
      brand: '',
      searchText: '',
      uploadText: 'Great! Please provide a banner file using JPEG, PNG, or SVG',
      fileName: '',
      allowedFormats: ['image/jpeg', 'image/png', 'image/svg+xml'],
      maxSize: 2 * 1024 * 1024,
      fileText: `Next, add news coverage links by pasting the URL's below.`,
      reportUrls: '',
      urlsSet: false,
      urlPlaceholder: `
www.techcrunch.com/article-1 
www.bloomberg.com/article-2
www.forbes.com/article-3
     `,
      lastInstructions: 'All set! We are now ready to run the report!',
      uploadedImageUrl: '',
    }
  },
  methods: {
    setUrls() {
      this.urlsSet = true
      this.scrollToChatTop()
    },
    uploadImage(event) {
      const file = event.target.files[0]

      if (!file) {
        this.fileName = ''
        alert('No file selected.')
        return
      }

      if (!this.allowedFormats.includes(file.type)) {
        alert('Only JPEG, PNG, and SVG files are allowed.')
        this.fileName = ''
        return
      }

      if (file.size > this.maxSize) {
        alert('File size should not exceed 2MB.')
        this.fileName = ''
        return
      }

      this.loading = true
      this.fileName = file.name
      this.scrollToChatTop()

      const reader = new FileReader()

      reader.onload = (e) => {
        const imageDataUrl = e.target.result
        this.uploadedImageUrl = imageDataUrl
        this.loading = false
      }

      reader.onerror = () => {
        alert('Error reading file.')
        this.fileName = ''
        this.loading = false
      }

      reader.readAsDataURL(file)
    },
    generateReportSearch() {
      if (!this.brand) {
        this.brand = this.searchText
        this.searchText = ''
        this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
        this.scrollToChatTop()
        return
      }
    },
    scrollToChatTop() {
      this.$nextTick(() => {
        const chatWindow = this.$refs.chatWindow
        chatWindow.scrollTop = chatWindow.scrollHeight
      })
    },
  },
  directives: {
    autoresize: {
      inserted(el) {
        function adjustTextareaHeight() {
          el.style.height = 'auto'
          el.style.height = el.scrollHeight + 'px'
        }

        el.addEventListener('input', adjustTextareaHeight)
        el.addEventListener('focus', adjustTextareaHeight)
        el.addEventListener('textarea-clear', function () {
          el.value = ''
          el.style.height = 'auto'
        })

        adjustTextareaHeight()
      },
    },

    typed: {
      bind(el, binding) {
        let text = binding.value
        let index = 0
        el.innerHTML = ''

        function type() {
          if (index < text.length) {
            el.innerHTML += text.charAt(index)
            index++
            setTimeout(type, 12)
          }
        }

        type()
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.thin-font {
  font-family: $thin-font-family;
}

.primary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: none;
  border-radius: 16px;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.flex-end {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.rotation {
  animation: rotation 2s infinite linear;
}

.file-input-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-family: $thin-font-family;
}

.file-input-label {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.file-input {
  display: none;
}

.large-input-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.025);
  border-radius: 28px;
  background-color: white;
  width: 100%;
  margin-bottom: 8px;

  @media only screen and (max-width: 600px) {
    width: 94vw !important;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    width: 70vw !important;
  }
}

.input-container-gray {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
  padding: 14px 0 12px 0;
  border-radius: 24px;
  width: 100%;
  color: $base-gray;
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  flex-direction: column;
  background-color: white;

  section {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    flex-direction: row;
  }

  img {
    filter: invert(40%);
  }
}

.area-input {
  width: 100%;
  margin-bottom: 0.25rem;
  max-height: 120px !important;
  padding: 0 1.25rem;
  line-height: 1.25;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $thin-font-family !important;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  background-color: transparent;
}
.area-input::-webkit-scrollbar {
  width: 4px;
  height: 0px;
}
.area-input::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.area-input::-webkit-scrollbar-track {
  margin-top: 24px;
}

.text-area-input {
  padding-top: 1rem;
}

input,
textarea {
  font-family: $thin-font-family;
}

input::placeholder {
  font-family: $thin-font-family;
}
input:disabled {
  cursor: not-allowed;
}
textarea:disabled {
  cursor: not-allowed;
}
textarea::placeholder {
  font-family: $thin-font-family;
}

.big-chat-bubble {
  width: fit-content;
  border-radius: 12px;
  padding: 8px 16px;
  margin: 12px 0;
  background-color: white;
  box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.05);
}

.space-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.reports {
  height: 100vh;
  width: 100vw;
  padding: 32px 20vw;
}
.chat-window {
  height: 96vh;
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: space-evenly;
  padding: 0 5vw;

  &__header {
    width: 100%;
    position: sticky;
    top: 0;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 32px 0 12px 0;
    p {
      font-family: $base-font-family;
      font-size: 18px !important;
    }
  }

  &__body {
    height: 100%;
    width: 100%;
    overflow-y: scroll;
    padding: 0 4px;
  }

  &__footer {
    position: sticky;
    bottom: 0;
    width: 100%;
    padding: 24px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    // border-top: 1px solid rgba(0, 0, 0, 0.1);
  }

  &__chat-bubble {
    line-height: 1.5;
    width: fit-content;
    border-radius: 20px;
    padding: 8px 16px;
    margin: 12px 0;
    background-color: white;
    box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.05);

    img {
      margin-right: 6px;
    }

    p {
      margin: 0;
    }
  }
}
</style>
