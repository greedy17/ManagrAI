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
                <button @click="getTrafficData" class="primary-button">Run report</button>
              </div>
            </div>
          </div>

          <div v-if="loading" class="space-between">
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
              <p v-typed="loadingText"></p>
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
          <div v-if="view === 'home'">
            <div style="padding-top: 20px" class="container">
              <div>
                <img :src="uploadedImageUrl" class="photo-header" />
              </div>

              <p>Executive overview for {{ brand }}</p>
              <pre v-html="summary" class="pre-text"></pre>
            </div>
          </div>

          <div v-else-if="view === 'charts'">
            <div class="container">
              <div class="space-between bottom-margin">
                <div class="col">
                  <p class="bold-font medium-txt">Total coverage</p>
                  <small>Number of news clips in this report</small>
                </div>

                <p class="bold-font">1000</p>
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
                  <p class="bold-font">100,000,000</p>
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
          <div v-else-if="view === 'starred'">
            <div class="container">
              <div class="container__top">
                <div style="margin-bottom: 8px">
                  <img src="@/assets/images/iconlogo.png" class="photo-header-small" />
                </div>

                <div class="space-between no-letter-margin">
                  <div class="col">
                    <p class="bold-font">Company</p>
                    <div style="margin-top: 8px" class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/profile.svg"
                        height="12px"
                        alt=""
                      />
                      <p>Journalist</p>
                    </div>
                  </div>
                  <small>1/11/2111</small>
                </div>

                <div>
                  <h3 style="margin: 16px 0" class="bold-font">
                    Lorem Ipsum filler text for an article headline
                  </h3>
                </div>

                <div class="space-between bottom-margin-m">
                  <div class="row small-text img-mar">
                    <img src="@/assets/images/users.svg" height="14px" alt="" />
                    <p class="bold-font">100,000,000</p>
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
          <div v-else-if="view === 'articles'">
            <div class="container">
              <div class="article">
                <div class="space-between">
                  <p class="bold-font">Outlet</p>
                  <img src="@/assets/images/star.svg" height="14px" alt="" />
                </div>

                <div class="space-between-bottom">
                  <div class="article-body">
                    <h3 class="bold-font">
                      Headline will be here lorem ipsum Headline will be here lorem ipsum Headline
                      will be here lorem ipsum Headline will be here lorem ipsum
                    </h3>

                    <p class="report-body">
                      Lorem ipsum simply dummy text of the printing and typesetting industry. Lorem
                      Ipsum has been the industry's standard dummy text ever since the 1500s, when
                      an unknown printer took a galley of type and scrambled it to make a type
                      specimen book. It has survived not only five centuries, but also the leap into
                      electronic typesetting, remaining essentially unchanged. It was popularised in
                      the 1960s with the release of Letraset sheets containing Lorem Ipsum passages,
                      and more recently with desktop publishing software like Aldus PageMaker
                      including versions of Lorem Ipsum.
                    </p>
                  </div>

                  <img src="@/assets/images/iconlogo.png" class="photo-header-alt" />
                </div>

                <div class="space-between">
                  <div class="row report-body">
                    <div class="pill">
                      <img src="@/assets/images/profile.svg" height="10px" alt="" />
                      <p style="margin-right: 4px">Journalist</p>
                    </div>

                    <small>10m</small>
                  </div>

                  <div class="row small-text img-mar">
                    <img src="@/assets/images/users.svg" height="14px" alt="" />
                    <p class="bold-font">100,000,000</p>
                  </div>
                </div>

                <div style="margin-top: 8px" class="space-between bottom-border">
                  <div></div>
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
      urlCount: 0,
      urls: [],
      loadingText: 'Generating report...',
      summary: `Executive Overview of Earned Media Report for Lululemon

1. Total Volume of Media Coverage and Trends in Mentions

Over the reporting period, Lululemon experienced significant media coverage with a notable increase in mentions during several key events. The total volume of coverage spiked at two specific points:

Product Launches: The unveiling of new product lines, particularly Lululemon's innovative "sweat-activated" workout gear and expansion into footwear, garnered widespread attention.
Partnership Announcements: Strategic partnerships, including collaborations with wellness influencers and global ambassadors, fueled spikes in mentions. The most prominent event was the announcement of a collaboration with a high-profile athlete, which drew heavy media and consumer interest.
Overall, mentions of Lululemon increased by 25% over the previous quarter, demonstrating growing media engagement. The bulk of this coverage originated from product-focused stories (60%), while the rest focused on the brand's sustainability initiatives and corporate leadership (40%).

2. Key Publications and Influential Journalists

Lululemon received coverage from a range of high-profile media outlets, underscoring the brand's strong presence in both business and lifestyle segments. Prominent publications included:

Forbes and The Wall Street Journal: Coverage focused on Lululemon's financial performance, market strategies, and expansion efforts.
Vogue, Harper's Bazaar, and Elle: These publications highlighted Lululemon's innovative designs, style appeal, and sustainability initiatives.
Men's Health and Women's Health: Articles centered on the functionality and benefits of Lululemon's performance apparel.
Several influential journalists covered the brand, amplifying its reach. Notably:

Vanessa Friedman, Fashion Director at The New York Times, wrote about Lululemon’s growing influence in the athleisure sector.
Emily Ratajkowski, contributing editor at Vogue, reviewed Lululemon’s latest activewear collection, praising its eco-friendly design.
Joe Pompliano, a sports business journalist, emphasized Lululemon's strategic athlete partnerships, positioning the brand as a dominant player in both fashion and performance wear.
3. Key Metrics: Reach, Impressions, and Engagement Rates

Lululemon's media presence generated significant exposure across various channels:

Total Reach: Coverage reached an estimated 500 million people globally, with high visibility across both North American and international markets.
Potential Impressions: The potential number of impressions reached 1.2 billion, driven by coverage in major publications, influential blogs, and social media platforms.
Engagement Rates: Lululemon's engagement rates were strong, particularly on social media where posts from news outlets and influencers about the brand saw an average engagement rate of 5%, surpassing the industry average of 3%. This was driven by interactive content, product reviews, and influencer partnerships.
4. Media Sentiment and Brand Image Impact

Media sentiment surrounding Lululemon was overwhelmingly positive. Approximately 85% of articles and posts portrayed the brand in a favorable light, with recurring themes of innovation, sustainability, and customer loyalty. Positive sentiment was driven by:

Product Quality: Media outlets consistently highlighted Lululemon's high-quality, durable, and stylish workout gear.
Sustainability: Many publications praised the brand’s efforts to implement sustainable practices, such as using recycled materials in new product lines and aiming for carbon neutrality by 2025.
Corporate Leadership: Coverage of CEO Calvin McDonald's leadership strategies received favorable reviews, positioning him as a key figure steering the brand’s growth and innovation.
However, about 10% of the coverage reflected neutral sentiment, mainly reporting on financial results or market competition, while 5% of the coverage carried a slightly negative tone. This negative sentiment arose from criticisms related to the high price point of Lululemon products and concerns from some media outlets about market oversaturation in the athleisure space. Despite this, the overall impact on Lululemon's brand image remains positive, reinforcing its position as a premium, innovative brand.

5. Recurring Themes and Key Messages

Several recurring themes emerged across the media coverage, shaping the narrative around Lululemon's brand:

Innovation in Product Development: The most frequent message was Lululemon’s commitment to product innovation, with features such as sweat-wicking materials, ergonomic designs, and the move into footwear garnering widespread attention.
Sustainability Leadership: Lululemon's dedication to sustainability was a major focal point. The media highlighted the brand’s eco-conscious practices, including the use of recycled fabrics and energy-efficient manufacturing processes.
Global Expansion and Growth: Stories about Lululemon’s international growth, especially in the Asian and European markets, showcased the brand’s ambitious expansion strategy, as well as its ability to maintain strong financial performance in competitive markets.
Health and Wellness Leadership: Media coverage frequently reinforced Lululemon's position as a lifestyle brand deeply connected to the health and wellness movement, appealing to a broad consumer base that values fitness, mental well-being, and mindful living.
Conclusion

Lululemon's recent media coverage reflects a strong brand presence driven by product innovation, sustainability efforts, and strategic leadership. The coverage trends and metrics indicate that the brand’s influence is expanding globally, with high levels of engagement and a largely positive sentiment. The focus on Lululemon’s innovation and leadership in both athleisure and wellness continues to elevate the brand’s image, ensuring its relevance in a competitive market.`,
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
    async getTrafficData() {
      this.loading = true
      this.scrollToChatTop()
      try {
        const res = await Comms.api.getTrafficData({
          urls: this.urls,
          // name: this.brand,
        })
        console.log(res)
        this.loading = false
        this.creating = false
      } catch (e) {
        console.error(e)
        this.loading = false
      } finally {
      }
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
      console.log(this.urls, this.urlCount)
    },
    processUrls(inputText) {
      // Split the input by commas and new lines, trim spaces around each split part
      const lines = inputText
        .split(/[\n,]+/)
        .map((line) => line.trim())
        .filter((line) => line !== '')
      const urls = []
      let count = 0

      // A set of valid TLDs (Top-Level Domains)
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
        // Add more TLDs as needed
      ])

      // Function to compute Levenshtein distance
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
                matrix[i - 1][j - 1] + 1, // substitution
                matrix[i][j - 1] + 1, // insertion
                matrix[i - 1][j] + 1, // deletion
              )
            }
          }
        }
        return matrix[b.length][a.length]
      }

      // Function to find the closest valid TLD
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
        // Only correct if the distance is 1 (e.g., '.con' -> '.com')
        return minDistance === 1 ? closestTLD : null
      }

      // Process each line or part
      for (let line of lines) {
        line = line.trim()
        if (line === '') continue // Skip empty entries

        // Extract the TLD from the URL
        const tldMatch = line.match(/\.([a-zA-Z]{2,})$/)
        if (tldMatch) {
          const tld = tldMatch[1].toLowerCase()
          if (!validTLDs.has(tld)) {
            // Attempt to correct the TLD
            const correctedTLD = findClosestTLD(tld)
            if (correctedTLD) {
              // Replace the incorrect TLD with the corrected one
              line = line.slice(0, -tld.length) + correctedTLD
            }
          }
        }
        urls.push(line)
        count++
      }

      // Return the list of URLs and the count
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
  padding: 2px 10px;
  margin-right: 8px;

  img {
    margin-right: 4px;
  }
  p {
    margin: 0 !important;
  }
}

.article {
  padding: 16px;
}

.article-body {
  margin-bottom: 12px;
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
  height: 150px;
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
