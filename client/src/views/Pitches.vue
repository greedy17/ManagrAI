<template>
  <div class="pitches">
    <div :class="{ opaque: loading }" v-if="!pitch" class="center">
      <p>Generate a pitch, blog post or press release based on any persona</p>

      <div class="input-container">
        <div class="input-row">
          <div class="main-text">
            <img src="@/assets/images/document.svg" height="14px" alt="" />
            Type
          </div>

          <input
            :disabled="loading"
            autofocus
            class="area-input"
            placeholder="Media Pitch, Blog Post, Press Release..."
            v-model="type"
          />
        </div>
      </div>
      <div class="input-container">
        <div class="input-row">
          <div class="main-text">
            <img src="@/assets/images/crown.svg" height="14px" alt="" />
            Brand
          </div>

          <input
            :disabled="loading"
            autofocus
            class="area-input"
            placeholder="FutureTech innovations, a leading innovator..."
            v-model="brand"
          />
        </div>
      </div>
      <div class="input-container">
        <div class="input-row">
          <div class="main-text">
            <img src="@/assets/images/target.svg" height="14px" alt="" />
            Persona
          </div>

          <input
            :disabled="loading"
            autofocus
            class="area-input"
            placeholder="Millenial tech enthusiast with a passion for healthcare..."
            v-model="persona"
          />
        </div>
      </div>
      <div class="input-container">
        <div class="input-row">
          <div class="main-text">
            <img src="@/assets/images/file-word.svg" height="14px" alt="" />
            Brief
          </div>

          <textarea
            :disabled="loading"
            autofocus
            class="area-input"
            placeholder="FutureTech Innovations is launching a cutting-edge smartwatch that not only measures vital signs but also predicts flu symptoms 48 hours in advance, using AI and biometric data…"
            v-model="briefing"
            v-autoresize
          />
        </div>
      </div>
      <div class="input-container">
        <div class="input-row">
          <div class="main-text">
            <img src="@/assets/images/comment.svg" height="14px" alt="" />
            Style
          </div>

          <textarea
            :disabled="loading"
            autofocus
            class="area-input"
            placeholder="Write a concise, engaging press release, highlighting the uniqueness of the product and its benefits to the target audience…"
            v-model="style"
            v-autoresize
          />
        </div>
      </div>

      <footer>
        <button :disabled="loading" @click="clearData" class="secondary-button">Clear</button>
        <button :disabled="loading" @click="generatePitch" class="primary-button">
          <img
            v-if="loading"
            class="rotate"
            height="14px"
            src="@/assets/images/loading.svg"
            alt=""
          />
          {{ loading ? 'Submitting' : 'Submit' }}
        </button>
      </footer>
    </div>

    <div v-else class="center">
      <div class="pitch-container">
        <div class="title-container">
          <h1 class="no-text-margin">{{ type }}</h1>
          <p class="sub-text">
            Target: <span>{{ persona }}</span>
          </p>
        </div>

        <div class="title-bar">
          <div class="row">
            <button class="secondary-button">Regenerate</button>
            <button class="primary-button">Save</button>
          </div>

          <div class="wrapper">
            <img
              style="cursor: pointer"
              class="right-mar"
              src="@/assets/images/clipboard.svg"
              height="18px"
              alt=""
            />
            <div style="margin-left: -20px" class="tooltip">Copy</div>
          </div>
        </div>

        <pre v-html="pitch" class="pre-text"></pre>
      </div>
    </div>
  </div>
</template>
<script>
import { Comms } from '@/services/comms'

export default {
  name: 'Pitches',
  components: {},
  data() {
    return {
      type: '',
      brand: '',
      persona: '',
      briefing: '',
      style: '',
      pitch: null,
      loading: false,
    }
  },
  watch: {},
  created() {},
  methods: {
    async generatePitch() {
      this.loading = true
      try {
        await Comms.api
          .generatePitch({
            type: this.type,
            brand: this.brand,
            persona: this.persona,
            briefing: this.briefing,
            style: this.style,
          })
          .then((response) => {
            this.pitch = response.pitch
          })
      } catch {
      } finally {
        // this.clearData()
        this.loading = false
      }
    },
    clearData() {
      this.type = ''
      this.brand = ''
      this.persona = ''
      this.briefing = ''
      this.style = ''
    },
  },
  computed: {},
  directives: {
    autoresize: {
      inserted(el) {
        function adjustTextareaHeight() {
          el.style.height = 'auto'
          el.style.height = el.scrollHeight + 'px'
        }

        el.addEventListener('input', adjustTextareaHeight)
        el.addEventListener('focus', adjustTextareaHeight)
        el.addEventListener('textarea-clear', adjustTextareaHeight)
        adjustTextareaHeight()
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

::placeholder {
  color: $mid-gray;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.title-container {
  width: 100%;
}

.no-text-margin {
  margin: 0;
}

.sub-text {
  color: $light-gray-blue;
  margin: 8px 0 0 0;
  font-size: 14px;
  font-weight: bold;
  font-family: $thin-font-family;
  span {
    font-weight: normal;
    word-wrap: break-word;
  }
}

.title-bar {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 24px 0 24px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.row {
  display: flex;
  align-items: center;
  flex-direction: row;

  button:first-of-type {
    margin-right: 1rem;
  }
}

.pitch-container {
  width: 50%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
}

.rotate {
  animation: rotation 2.25s infinite linear;
  cursor: not-allowed;

  margin-right: 8px;
}

.pre-text {
  background-color: $white-blue;
  border-radius: 4px;
  padding: 16px;
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.pitches {
  background-color: white;
  width: 100vw;
  height: 100vh;
  padding: 58px 36px 0 36px;
  display: flex;
  overflow-y: scroll;
  font-family: $base-font-family;
  color: $chat-font-color;
}

.center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  height: 100%;
  padding-top: 32px;
  font-size: 14px;
  color: $dark-black-blue;
  gap: 24px;
}

.input-container {
  flex-wrap: nowrap;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.75rem 1.2rem 0.75rem 1.2rem;
  border-radius: 6px;
  width: 600px;
  background-color: $offer-white;
  color: $base-gray;
}
.area-input {
  width: 100%;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0 1.25rem;
  line-height: 1.75;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 13px;
  font-family: $base-font-family;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
}

.area-input:disabled {
  cursor: not-allowed;
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
.input-row {
  display: flex;
  align-items: center;
  flex-direction: row;
  align-items: center;
}
.main-text {
  width: 80px;
  display: flex;
  flex-direction: row;
  align-items: center;
  white-space: nowrap;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  padding-right: 1rem;
  margin: 0;
  font-size: 13px;
  color: $dark-black-blue;
  svg,
  img {
    margin-right: 8px;
    filter: invert(40%);
  }
}

footer {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  padding-bottom: 1rem;
}

.primary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: none;
}

.secondary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: $dark-black-blue;
  background-color: white;
  margin-right: -2px;
}

.opaque {
  opacity: 0.75;
}

.wrapper {
  display: flex;
  align-items: center;
  // background-color: red;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip {
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: -20px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 100px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

/* This bridges the gap so you can mouse into the tooltip without it disappearing */
.wrapper .tooltip:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-top: solid $dark-black-blue 10px;
  bottom: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper .tooltip {
  display: none;
}

.lte8 .wrapper:hover .tooltip {
  display: block;
}
</style>