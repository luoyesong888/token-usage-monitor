import Foundation

enum DeepSeekClientError: LocalizedError {
    case invalidAPIKey
    case invalidResponse
    case server(String)

    var errorDescription: String? {
        switch self {
        case .invalidAPIKey: return "DeepSeek API Key 为空或格式不正确。"
        case .invalidResponse: return "DeepSeek 返回了无法识别的数据。"
        case .server(let message): return message
        }
    }
}

private struct DeepSeekBalanceResponse: Decodable {
    var isAvailable: Bool
    var balanceInfos: [DeepSeekBalanceInfo]
}

private struct DeepSeekModelsResponse: Decodable {
    struct Model: Decodable { var id: String }
    var data: [Model]
}

private struct DeepSeekErrorEnvelope: Decodable {
    struct APIError: Decodable { var message: String? }
    var error: APIError?
}

struct DeepSeekClient {
    private let apiKey: String
    private let session: URLSession
    private let baseURL = URL(string: "https://api.deepseek.com")!

    init(apiKey: String) throws {
        let cleaned = apiKey.trimmingCharacters(in: .whitespacesAndNewlines)
        guard cleaned.count >= 8 else { throw DeepSeekClientError.invalidAPIKey }
        self.apiKey = cleaned
        let configuration = URLSessionConfiguration.ephemeral
        configuration.timeoutIntervalForRequest = 20
        configuration.timeoutIntervalForResource = 30
        configuration.waitsForConnectivity = false
        session = URLSession(configuration: configuration)
    }

    func fetchAccountSnapshot() async throws -> DeepSeekAccountSnapshot {
        async let balanceData = request(path: "user/balance")
        async let modelsData = request(path: "models")
        let (balancePayload, modelPayload) = try await (balanceData, modelsData)

        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        guard let balance = try? decoder.decode(DeepSeekBalanceResponse.self, from: balancePayload),
              let models = try? decoder.decode(DeepSeekModelsResponse.self, from: modelPayload) else {
            throw DeepSeekClientError.invalidResponse
        }
        return DeepSeekAccountSnapshot(
            isAvailable: balance.isAvailable,
            balances: balance.balanceInfos,
            models: models.data.map(\.id).sorted(),
            updatedAt: Date()
        )
    }

    private func request(path: String) async throws -> Data {
        let url = path.split(separator: "/").reduce(baseURL) {
            $0.appendingPathComponent(String($1))
        }
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else { throw DeepSeekClientError.invalidResponse }
        guard (200..<300).contains(http.statusCode) else {
            let decoder = JSONDecoder()
            let detail = (try? decoder.decode(DeepSeekErrorEnvelope.self, from: data))?.error?.message
            if http.statusCode == 401 || http.statusCode == 403 {
                throw DeepSeekClientError.server(detail ?? "DeepSeek API Key 验证失败。")
            }
            throw DeepSeekClientError.server(detail ?? "DeepSeek 请求失败（HTTP \(http.statusCode)）。")
        }
        return data
    }
}
