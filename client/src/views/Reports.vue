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
                  @input="handleInput"
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
              <p>{{ urlCount }} Urls uploaded</p>
            </div>
          </div>

          <div v-if="urlsSet">
            <div class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="lastInstructions"></p>
              </div>

              <div style="margin: 0 0 8px 8px">
                <button @click="getReportClips" class="primary-button">Run report</button>
              </div>
            </div>
          </div>

          <div v-if="loading" class="space-between">
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
              <p style="margin-right: 6px">{{ loadingText }}</p>
              <img class="rotation" src="@/assets/images/loading.svg" height="14px" alt="" />
            </div>
            <div></div>
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
                  v-if="searchText"
                  @click="generateReportSearch($event)"
                  class="left-margin pointer lite-bg img-container-stay-alt"
                  style="margin-right: 24px"
                >
                  <img
                    style="margin: 0"
                    src="@/assets/images/paper-plane-full.svg"
                    height="14px"
                    alt=""
                  />
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="fadein" v-else>
      <div v-if="loading">loading here</div>

      <div v-else class="chat-window">
        <div class="chat-window__header">
          <p class="thin-font">
            <span class="bold-font">{{ brand }}</span> Coverage Report
          </p>
          <div class="row">
            <button class="secondary-button">Share</button>
            <button class="primary-button">Save</button>
            <!-- <img src="@/assets/images/disk.svg" height="14px" alt="" /> -->
          </div>
        </div>

        <div class="chat-window__body">
          <div class="fadein" v-if="view === 'home'">
            <div style="padding-top: 20px" class="container">
              <div>
                <img :src="uploadedImageUrl" class="photo-header" />
              </div>
              <!-- <p>Executive overview for {{ brand }}</p> -->
              <pre v-html="summary" class="pre-text"></pre>
            </div>
          </div>

          <div class="fadein" v-else-if="view === 'charts'">
            <div class="container">
              <div class="space-between bottom-margin">
                <div class="col">
                  <p class="bold-font medium-txt">Total coverage</p>
                  <small>Number of news clips in this report</small>
                </div>

                <p class="bold-font">{{ urlCount }}</p>
              </div>

              <div class="space-between bottom-margin">
                <div class="col">
                  <p class="bold-font medium-txt">Unique visitors</p>
                  <small>The potential audience reached by your media coverage</small>
                </div>

                <div class="row">
                  <img
                    style="margin-right: 8px"
                    src="@/assets/images/users.svg"
                    height="16px"
                    alt=""
                  />
                  <p class="bold-font">{{ formatNumber(totalVisits) }}</p>
                </div>
              </div>

              <div class="space-between">
                <div class="col">
                  <p class="bold-font medium-txt">Total shares</p>
                  <small>Number of times content was shared on social media</small>
                </div>

                <section class="rows">
                  <div class="row">
                    <img src="@/assets/images/facebook.png" height="20px" alt="" />
                    <p class="bold-font">10,000</p>
                  </div>
                  <div class="row">
                    <img src="@/assets/images/twitter-x.svg" height="16px" alt="" />
                    <p class="bold-font">1,000</p>
                  </div>
                  <div class="row">
                    <img src="@/assets/images/reddit.svg" height="20px" alt="" />
                    <p class="bold-font">10,000</p>
                  </div>
                  <div class="row">
                    <img src="@/assets/images/pinterest.png" height="20px" alt="" />
                    <p class="bold-font">100</p>
                  </div>
                </section>
              </div>
            </div>

            <div class="container">
              <div class="col">
                <p class="bold-font medium-txt">Media exposure over time</p>
                <small
                  >Number of media clips <span class="bold-font">per month</span> along with the
                  potential reach</small
                >
              </div>
              <ReportLineChart />
            </div>
          </div>
          <div class="fadein" v-else-if="view === 'starred'">
            <div v-for="(article, i) in starredArticles" :key="i" class="container">
              <div class="container__top">
                <div style="margin-bottom: 12px">
                  <img
                    @error="onImageError($event)"
                    :src="article.image"
                    class="photo-header-small"
                  />
                </div>

                <div class="space-between no-letter-margin">
                  <div class="col">
                    <p class="bold-font">{{ article.source }}</p>
                    <div style="margin-top: 8px" class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/profile.svg"
                        height="12px"
                        alt=""
                      />
                      <p>{{ article.author[0] ? article.author[0] : 'Unkown' }}</p>
                    </div>
                  </div>
                  <small>{{ getTimeDifferenceInMinutes(article.date) }}</small>
                </div>

                <div>
                  <h3 style="margin: 16px 0" class="bold-font">
                    {{ article.description }}
                  </h3>
                </div>

                <div class="space-between bottom-margin-m">
                  <div class="row img-mar">
                    <img src="@/assets/images/users.svg" height="14px" alt="" />
                    <p class="bold-font">{{ formatNumber(article.traffic.visits) }}</p>
                  </div>

                  <section class="row-even small-text img-mar">
                    <div class="row">
                      <img src="@/assets/images/facebook.png" height="14px" alt="" />
                      <p class="bold-font">10,000</p>
                    </div>
                    <div class="row">
                      <img src="@/assets/images/twitter-x.svg" height="12px" alt="" />
                      <p class="bold-font">1,000</p>
                    </div>
                    <div class="row">
                      <img src="@/assets/images/reddit.svg" height="14px" alt="" />
                      <p class="bold-font">10,000</p>
                    </div>
                    <div class="row">
                      <img src="@/assets/images/pinterest.png" height="14px" alt="" />
                      <p class="bold-font">100</p>
                    </div>
                  </section>
                </div>
              </div>

              <div class="report-body">
                <div style="margin-top: 12px">
                  <p class="bold-font">Summary</p>
                  <p>
                    Lorem ipsum simply dummy text of the printing and typesetting industry. Lorem
                    Ipsum has been the industry's standard dummy text ever since the 1500s, when an
                    unknown printer took a galley of type and scrambled it to make a type specimen
                    book. It has survived not only five centuries, but also the leap into electronic
                    typesetting, remaining essentially unchanged. It was popularised in the 1960s
                    with the release of Letraset sheets.
                  </p>
                </div>
                <div style="margin-top: 12px">
                  <p class="bold-font">Sentiment</p>
                  <p>
                    Lorem ipsum is simply dummy text of the printing and typesetting industry. Lorem
                    Ipsum has been the industry's standard dummy text ever since the 1500s, when an
                    unknown printer took a galley of type and scrambled it to make a type specimen
                    book. It has survived not only five centuries, but also the leap into electronic
                    typesetting, remaining essentially unchanged.
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="fadein" v-else-if="view === 'articles'">
            <div class="container">
              <div v-for="(article, i) in clips" :key="i" class="article">
                <div class="space-between">
                  <p class="bold-font">{{ article.source }}</p>
                  <img src="@/assets/images/star.svg" height="14px" alt="" />
                </div>

                <div class="space-between-bottom">
                  <div class="article-body">
                    <h3 class="bold-font">
                      {{ article.title }}
                    </h3>

                    <p class="report-body">
                      {{ article.description }}
                    </p>
                  </div>

                  <img
                    @error="onImageError($event)"
                    :src="article.image"
                    class="photo-header-alt"
                  />
                </div>

                <div style="margin-top: 12px" class="space-between">
                  <div class="row report-body">
                    <div class="pill">
                      <img src="@/assets/images/profile.svg" height="12px" alt="" />
                      <p style="margin-right: 6px">
                        {{ article.author[0] ? article.author[0] : 'Unkown' }}
                      </p>
                    </div>

                    <small>{{ getTimeDifferenceInMinutes(article.date) }}</small>
                  </div>

                  <div class="row img-mar">
                    <img
                      style="margin-right: 4px"
                      src="@/assets/images/users.svg"
                      height="14px"
                      alt=""
                    />
                    <p style="font-size: 14px" class="bold-font">
                      {{ formatNumber(article.traffic.visits) }}
                    </p>
                  </div>
                </div>

                <div style="margin-top: 8px" class="space-between bottom-border">
                  <div></div>
                  <section class="row-even small-text img-mar">
                    <div class="row">
                      <img src="@/assets/images/facebook.png" height="14px" alt="" />
                      <p class="bold-font">{{ formatNumber(article.traffic.social / 2) }}</p>
                    </div>
                    <div class="row">
                      <img src="@/assets/images/twitter-x.svg" height="12px" alt="" />
                      <p class="bold-font">{{ formatNumber(article.traffic.social / 2) }}</p>
                    </div>
                    <div class="row">
                      <img src="@/assets/images/reddit.svg" height="14px" alt="" />
                      <p class="bold-font">{{ formatNumber(article.traffic.social / 4) }}</p>
                    </div>
                    <div class="row">
                      <img src="@/assets/images/pinterest.png" height="14px" alt="" />
                      <p class="bold-font">{{ formatNumber(article.traffic.social / 8) }}</p>
                    </div>
                  </section>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <nav v-if="!creating" class="left-nav">
      <ul class="nav-links">
        <li @click="changeView('home')" class="nav-item">
          <div :class="{ active: view === 'home' }">
            <img src="@/assets/images/home.svg" height="16px" alt="" />
          </div>
        </li>
        <li @click="changeView('charts')" class="nav-item">
          <div :class="{ active: view === 'charts' }">
            <img src="@/assets/images/stats.svg" height="16px" alt="" />
          </div>
        </li>
        <li @click="changeView('starred')" class="nav-item">
          <div :class="{ active: view === 'starred' }">
            <img src="@/assets/images/star.svg" height="16px" alt="" />
          </div>
        </li>
        <li @click="changeView('articles')" class="nav-item">
          <div :class="{ active: view === 'articles' }">
            <img src="@/assets/images/report.svg" height="16px" alt="" />
          </div>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script>
import ReportLineChart from '@/components/ReportLineChart.vue'
import { Comms } from '@/services/comms'

export default {
  name: 'Reports',
  components: {
    ReportLineChart,
  },
  data() {
    return {
      socialData: null,
      totalVisits: 0,
      starredArticles: [],
      logoPlaceholder: require('@/assets/images/iconlogo.png'),
      traffic: null,
      urlCount: 0,
      urls: [],
      clips: [],
      loadingText: 'Analyzing articles...',
      summary: '',
      view: 'home',
      creating: true,
      brandText: 'Using the message bar, tell us which brand this report is for',
      loading: false,
      brand: '',
      searchText: '',
      uploadText: 'Great! Please provide a banner file using JPEG, PNG, or SVG',
      fileName: '',
      allowedFormats: [
        'image/jpeg',
        'image/png',
        'image/svg+xml',
        'image/webp',
        'image/gif',
        'image/tiff',
        'image/bmp',
        'application/pdf',
      ],
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
    getTimeDifferenceInMinutes(dateString) {
      if (dateString) {
        const currentDate = new Date()
        const givenDate = new Date(dateString)

        if (
          givenDate.getDate() === currentDate.getDate() &&
          givenDate.getMonth() === currentDate.getMonth() &&
          givenDate.getFullYear() === currentDate.getFullYear()
        ) {
          const timeDifferenceInMilliseconds = currentDate - givenDate
          const timeDifferenceInMinutes = Math.floor(timeDifferenceInMilliseconds / (1000 * 60))
          if (timeDifferenceInMinutes >= 60) {
            const timeDifferenceInHours = Math.floor(timeDifferenceInMinutes / 60)
            const remainingMinutes = timeDifferenceInMinutes % 60
            return `${timeDifferenceInHours}h`
          } else {
            return `${timeDifferenceInMinutes}m`
          }
        } else {
          let month
          let day
          let year
          if (Number(givenDate.getMonth() + 1)) {
            month = givenDate.getMonth() + 1
          } else {
            month = '--'
          }
          if (Number(givenDate.getDate())) {
            day = givenDate.getDate()
          } else {
            day = '--'
          }
          if (Number(givenDate.getFullYear())) {
            year = givenDate.getFullYear()
          } else {
            year = '--'
          }
          return `${month}/${day}/${year}`
        }
      } else {
        return '--/--/----'
      }
    },
    formatNumber(number) {
      // Round the number up using Math.ceil to remove decimals
      const roundedNumber = Math.ceil(number)

      // Convert the number to a string and format it with commas
      return roundedNumber.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    },
    onImageError(event) {
      event.target.src = this.logoPlaceholder
    },
    async getReportClips() {
      this.loading = true
      this.scrollToChatTop()
      try {
        const res = await Comms.api.getReportClips({
          urls: this.urls,
        })
        this.clips = res
        this.getReportSummary()
      } catch (e) {
        console.error(e)
        this.loadingText = 'Analyzing articles...'
        this.loading = false
      }
    },
    async getReportSummary() {
      this.loadingText = 'Summarizing data...'
      try {
        const res = await Comms.api.getReportSummary({
          clips: this.clips,
          brand: this.brand,
        })
        this.summary = res.summary
          .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
          .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
        this.getTrafficData()
      } catch (e) {
        console.error(e)
        this.loading = false
        this.loadingText = 'Analyzing articles...'
      }
    },
    async getTrafficData() {
      this.loadingText = 'Gathering traffic...'
      try {
        const res = await Comms.api.getTrafficData({
          urls: this.urls,
        })
        this.traffic = res
        this.getSocialData()
      } catch (e) {
        console.error(e)
        this.loadingText = 'Analyzing articles...'
        this.loading = false
      }
    },
    async getSocialData() {
      this.loadingText = 'Generating report...'
      try {
        const res = await Comms.api.getSocialData({
          urls: this.urls,
        })
        console.log(res)
        this.socialData = res
        this.combineArticlesWithTraffic()
        this.loading = false
        this.creating = false
        this.loadingText = 'Analyzing articles...'
      } catch (e) {
        console.error(e)
        this.loadingText = 'Analyzing articles...'
        this.loading = false
      }
    },
    combineArticlesWithTraffic() {
      this.clips = this.clips.map((article) => {
        const domain = article.source.replace(/^https?:\/\//, '').replace(/^www\./, '')
        const traffic = this.traffic[domain] || null
        return {
          ...article,
          traffic,
        }
      })
      this.totalVisits = this.calculateTotalVisits()
      this.starredArticles.push(this.clips[0])
      console.log('NEW CLIPS ARE HERE ==== >', this.clips)
    },
    calculateTotalVisits() {
      let totalVisits = 0
      for (let key in this.traffic) {
        if (this.traffic[key].visits) {
          totalVisits += parseInt(this.traffic[key].visits)
        }
      }
      return totalVisits
    },
    async runReport() {
      this.loading = true
      try {
        const res = await Comms.api.runReport({
          urls: this.urls,
          name: this.brand,
        })
        console.log(res)
        this.loading = false
      } catch (e) {
        console.error(e)
        this.loading = false
      } finally {
      }
    },
    handleInput() {
      const result = this.processUrls(this.reportUrls)
      this.urls = result.urls
      this.urlCount = result.count
    },
    processUrls(inputText) {
      const lines = inputText
        .split(/[\n,]+/)
        .map((line) => line.trim())
        .filter((line) => line !== '')
      const urls = []
      let count = 0

      const validTLDs = new Set([
        'com',
        'org',
        'net',
        'int',
        'edu',
        'gov',
        'mil',
        'co',
        'io',
        'me',
        'biz',
        'info',
        'xyz',
        'online',
        'site',
        'club',
        'shop',
        'blog',
        'web',
        'art',
        'app',
        'dev',
        'tech',
        'store',
        'ai',
        'us',
        'uk',
      ])

      function levenshteinDistance(a, b) {
        const matrix = []
        let i
        for (i = 0; i <= b.length; i++) {
          matrix[i] = [i]
        }
        let j
        for (j = 0; j <= a.length; j++) {
          matrix[0][j] = j
        }
        for (i = 1; i <= b.length; i++) {
          for (j = 1; j <= a.length; j++) {
            if (b.charAt(i - 1) === a.charAt(j - 1)) {
              matrix[i][j] = matrix[i - 1][j - 1]
            } else {
              matrix[i][j] = Math.min(
                matrix[i - 1][j - 1] + 1,
                matrix[i][j - 1] + 1,
                matrix[i - 1][j] + 1,
              )
            }
          }
        }
        return matrix[b.length][a.length]
      }

      function findClosestTLD(tld) {
        let minDistance = Infinity
        let closestTLD = null
        for (let validTLD of validTLDs) {
          const distance = levenshteinDistance(tld, validTLD)
          if (distance < minDistance) {
            minDistance = distance
            closestTLD = validTLD
          }
        }
        return minDistance === 1 ? closestTLD : null
      }

      for (let line of lines) {
        line = line.trim()
        if (line === '') continue

        const tldMatch = line.match(/\.([a-zA-Z]{2,})$/)
        if (tldMatch) {
          const tld = tldMatch[1].toLowerCase()
          if (!validTLDs.has(tld)) {
            const correctedTLD = findClosestTLD(tld)
            if (correctedTLD) {
              line = line.slice(0, -tld.length) + correctedTLD
            }
          }
        }
        urls.push(line)
        count++
      }

      return { urls, count }
    },

    changeView(txt) {
      this.view = txt
    },
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

.fadein {
  transition: opacity 1s ease-out;
  opacity: 0;
  animation: fadeIn 1s forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

.bottom-border {
  border-bottom: 2px solid rgba(0, 0, 0, 0.05);
  padding-bottom: 12px;
}

.pill {
  display: flex;
  flex-direction: row;
  align-items: center;
  background-color: $soft-gray;
  border-radius: 16px;
  padding: 3px 10px;
  margin-right: 8px;

  img {
    margin-right: 4px;
  }
  p {
    margin: 0 !important;
    font-size: 14px;
  }
}

.article {
  padding: 16px;
}

.article-body {
  margin-bottom: 12px;
  margin-right: 32px;
  width: 100%;
  max-height: 150px;
  overflow: hidden;

  h3 {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .report-body {
    height: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.report-body {
  font-family: $thin-font-family;
  line-height: 1.5;
  font-size: 14px;
}

.no-letter-margin {
  p {
    margin: 0 !important;
  }
}

.img-mar {
  img {
    margin-right: 4px;
  }
}

.small-text {
  font-size: 13px;
}

.medium-txt {
  font-size: 18px;
}

.bottom-margin {
  margin-bottom: 24px;
}

.bottom-margin-m {
  margin-bottom: 12px;
}

.container {
  background-color: white;
  padding: 16px;
  border-radius: 9px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;
  font-family: $thin-font-family;
  p {
    margin: 8px 0;
  }

  small {
    color: $base-gray;
  }

  &__top {
    border-bottom: 2px solid rgba(0, 0, 0, 0.05);
  }
}

.col {
  display: flex;
  flex-direction: column;
}

.active {
  background-color: $soft-gray;
}

.pre-text {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

::v-deep .pre-text {
  a {
    color: $grape;
    border-bottom: 1px solid $grape;
    font-family: $base-font-family;
    text-decoration: none;
    padding-bottom: 2px;

    &:hover {
      opacity: 0.7;
    }
  }

  strong,
  h1,
  h2,
  h3 {
    font-family: $base-font-family;
  }

  ul {
    display: block;
    list-style-type: disc;
    margin-block-start: 0;
    margin-block-end: 0;
    margin-inline-start: 0px;
    margin-inline-end: 0px;
    padding-inline-start: 16px;
    unicode-bidi: isolate;
  }

  li {
    // margin-top: -32px;
    padding: 0;
  }
}

.photo-header-alt {
  height: 150px;
  width: 150px;
  margin: 0;
  object-fit: cover;
  border-radius: 4px;
}

.space-between-bottom {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-end;
  width: 100%;
}

.photo-header {
  height: 250px;
  width: 100%;
  margin: 0;
  object-fit: cover;
  border-radius: 5px;
}

.photo-header-small {
  height: 250px;
  width: 100%;
  margin: 0;
  object-fit: cover;
  border-radius: 5px;
}

.left-nav {
  width: 60px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  background-color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  // box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);

  .nav-links {
    list-style: none;
    padding: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    .nav-item {
      margin: 10px 0;
      display: flex;
      justify-content: center;
      cursor: pointer;

      div {
        padding: 9px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        transition: background 0.3s ease;
        &:hover {
          background-color: $soft-gray;
        }

        img {
          margin: 0;
        }
      }
    }
  }
}

.thin-font {
  font-family: $thin-font-family !important;
}

.bold-font {
  font-family: $base-font-family !important;
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

.row-even {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  width: 50%;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.rows {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 4px 0;

  div {
    width: 40%;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-end;
    // padding-left: 12px;

    img {
      margin-right: 8px;
    }
  }
}

.reports {
  height: 100vh;
  width: 100vw;
  padding: 32px 18vw;
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
    padding: 48px 0 12px 0;
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
