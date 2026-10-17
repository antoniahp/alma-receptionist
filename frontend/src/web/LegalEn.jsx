// English translation of the legal pages. The Spanish version is the one that counts legally:
// these texts are a template the owner must review with her advisor before publishing.

function Missing({ children }) {
  return <mark className="legal-missing">{children}</mark>
}

function Owner({ info }) {
  return (
    <ul>
      <li><b>Owner:</b> {info.legal_name || <Missing>full name or company name</Missing>}</li>
      <li><b>Tax ID (NIF):</b> {info.nif || <Missing>NIF</Missing>}</li>
      <li><b>Address:</b> {info.address}</li>
      <li><b>Phone:</b> {info.phone}</li>
      <li><b>Email:</b> {info.email ? <a href={`mailto:${info.email}`}>{info.email}</a> : <Missing>contact email</Missing>}</li>
    </ul>
  )
}

function LegalNotice({ info }) {
  return (
    <>
      <h1>Legal notice</h1>
      <p>As required by Spanish Law 34/2002 on information society services and e-commerce (LSSI-CE), these are the details of who runs this website:</p>
      <Owner info={info} />
      <h2>What this website is for</h2>
      <p>To show the treatments and prices of {info.name} and let you book an appointment, either on the website or by talking to {info.assistant_name}, the salon’s virtual receptionist.</p>
      <h2>Prices</h2>
      <p>Prices shown are final and include VAT. They may change; the price you booked at is always respected.</p>
      <h2>Virtual receptionist</h2>
      <p>{info.assistant_name} is an automated program, not a person. It answers with the salon’s information and, when it doesn’t know something, passes it on to {info.owner}. Its answers are for guidance only and are not medical advice.</p>
      <h2>Intellectual property</h2>
      <p>The texts, logo and images on this website belong to their owner and may not be copied without permission.</p>
      <h2>Liability</h2>
      <p>We try to keep the information correct and up to date, but mistakes can happen. If you spot one, tell us and we’ll fix it.</p>
      <h2>Applicable law</h2>
      <p>This website is governed by Spanish law.</p>
    </>
  )
}

function Privacy({ info }) {
  return (
    <>
      <h1>Privacy policy</h1>
      <p>A plain explanation of which of your data we use and why, under the EU General Data Protection Regulation (GDPR) and Spanish Organic Law 3/2018 (LOPDGDD).</p>

      <h2>Who is responsible for your data</h2>
      <Owner info={info} />

      <h2>What data we use</h2>
      <ul>
        <li><b>To book:</b> your name and mobile number, the treatment and the time.</li>
        <li><b>If you use Telegram:</b> your Telegram chat ID and the messages you send us.</li>
        <li><b>If you use the chat on the website:</b> the messages in that conversation.</li>
        <li><b>If you tell us:</b> notes to look after you properly, such as allergies or skin type. This is health data: we only write it down if you give it to us, and only to carry out the treatment safely.</li>
        <li><b>Your history with the salon:</b> appointments, packs and how you paid, because the law requires it for the accounts.</li>
      </ul>
      <p>We don’t ask for more data than we need and we don’t use it for advertising profiles.</p>

      <h2>Why we use it and on what legal basis</h2>
      <ul>
        <li><b>Managing your appointments</b> (booking, reminding you, changing or cancelling them): because you ask for it when you book (Art. 6.1.b GDPR).</li>
        <li><b>Letting you know when a treatment is due again</b> and, only once after several visits, <b>asking for a Google review</b>: the salon’s legitimate interest in looking after its clients. If you don’t want these messages, tell {info.owner} and they will stop.</li>
        <li><b>Health notes</b>: with your explicit consent (Art. 9.2.a GDPR), which you can withdraw at any time.</li>
        <li><b>Accounting and tax obligations</b>: legal obligation (Art. 6.1.c GDPR).</li>
      </ul>

      <h2>The virtual receptionist</h2>
      <p>
        {info.assistant_name} uses an open-source artificial intelligence model to understand your messages and reply.
        It doesn’t make decisions for you: it only gives information and books what you ask for. If you’d rather talk to a person, say so and {info.owner} will reply.
      </p>

      <h2>Who else sees your data</h2>
      <p>
        Nobody else, except the providers we need to make this work, who only process it on our behalf:
        the website hosting service, the AI service that reads chat messages and, if you use it, Telegram.
        We don’t sell or share your data. We would only hand it to the authorities if the law required it.
      </p>

      <h2>How long we keep it</h2>
      <ul>
        <li>Your client details, notes and conversations: for as long as you keep coming to the salon, or until you ask us to delete them.</li>
        <li>Payment records: for the years tax law requires. If you ask us to delete your data, they are kept without your name.</li>
      </ul>

      <h2>Your rights</h2>
      <p>
        You can ask to see your data, correct it, delete it, take it with you, restrict its use or object to it.
        Write to {info.email ? <a href={`mailto:${info.email}`}>{info.email}</a> : <Missing>contact email</Missing>}, call {info.phone} or tell us at the salon.
        We’ll reply within a month. If you think we haven’t handled it properly, you can complain to the
        {' '}<a href="https://www.aepd.es" target="_blank" rel="noreferrer">Spanish Data Protection Agency (AEPD)</a>.
      </p>
    </>
  )
}

function Cookies({ info }) {
  return (
    <>
      <h1>Cookie policy</h1>
      <p>This website <b>does not use advertising or analytics cookies</b> and does not track you across other sites. That’s why you don’t see the usual cookie banner.</p>
      <h2>What we store in your browser</h2>
      <ul>
        <li><b>Clients:</b> your language choice (Spanish or English) and an identifier of your conversation with {info.assistant_name}, so she recognises you if you come back. Your messages and data are not stored in the browser: they are kept by the salon. Both are needed for the chat to work.</li>
        <li><b>Salon panel:</b> when {info.owner} logs in to her panel, the browser keeps her session so she isn’t asked for the password every time. This is strictly necessary and needs no consent (Art. 22.2 LSSI-CE).</li>
      </ul>
      <h2>Links to other websites</h2>
      <p>If you open Google Maps, Telegram or Google to leave a review, those sites have their own cookies and policies.</p>
    </>
  )
}

export const PAGES_EN = { 'aviso-legal': LegalNotice, privacidad: Privacy, cookies: Cookies }
